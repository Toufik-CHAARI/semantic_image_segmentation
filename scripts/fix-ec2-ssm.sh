#!/bin/bash
set -e

echo "🔧 Fixing EC2 instance SSM configuration..."

# Get EC2 instance ID from environment or prompt
if [ -z "$EC2_INSTANCE_ID" ]; then
    echo "Please enter your EC2 instance ID:"
    read EC2_INSTANCE_ID
fi

echo "Using EC2 instance ID: $EC2_INSTANCE_ID"

# Deploy CloudFormation stack to create IAM role and instance profile
echo "📦 Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file aws/ec2-ssm-setup.yml \
    --stack-name ec2-ssm-setup \
    --parameter-overrides EC2InstanceId=$EC2_INSTANCE_ID \
    --capabilities CAPABILITY_NAMED_IAM \
    --region eu-west-3

# Get the instance profile ARN
INSTANCE_PROFILE_ARN=$(aws cloudformation describe-stacks \
    --stack-name ec2-ssm-setup \
    --query 'Stacks[0].Outputs[?OutputKey==`InstanceProfileArn`].OutputValue' \
    --output text \
    --region eu-west-3)

echo "Instance Profile ARN: $INSTANCE_PROFILE_ARN"

# Stop the EC2 instance to attach the instance profile
echo "⏸️ Stopping EC2 instance to attach IAM role..."
aws ec2 stop-instances --instance-ids $EC2_INSTANCE_ID --region eu-west-3

# Wait for instance to stop
echo "⏳ Waiting for instance to stop..."
aws ec2 wait instance-stopped --instance-ids $EC2_INSTANCE_ID --region eu-west-3

# Attach the instance profile
echo "🔗 Attaching instance profile..."
aws ec2 modify-instance-attribute \
    --instance-id $EC2_INSTANCE_ID \
    --iam-instance-profile "Name=EC2SSMInstanceProfile" \
    --region eu-west-3

# Start the instance
echo "▶️ Starting EC2 instance..."
aws ec2 start-instances --instance-ids $EC2_INSTANCE_ID --region eu-west-3

# Wait for instance to start
echo "⏳ Waiting for instance to start..."
aws ec2 wait instance-running --instance-ids $EC2_INSTANCE_ID --region eu-west-3

# Wait a bit more for SSM agent to be ready
echo "⏳ Waiting for SSM agent to be ready..."
sleep 60

# Test SSM connectivity
echo "🧪 Testing SSM connectivity..."
aws ssm describe-instance-information \
    --filters "Key=InstanceIds,Values=$EC2_INSTANCE_ID" \
    --region eu-west-3

echo "✅ EC2 instance SSM configuration fixed!"
echo "🌐 Your EC2 instance should now be ready for automated deployment."
echo "📋 Next time you push to master, the CI/CD pipeline should successfully deploy to EC2."
