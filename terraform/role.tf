
# resource "aws_iam_role" "lambda_role" {
#   name = "lambda_role"
#   assume_role_policy = <<EOF
# {
#   "Version": "2012-10-17",
#   "Statement": [
#     {
#       "Effect": "Allow",
#       "Principal": { "Service": "lambda.amazonaws.com" },
#       "Action": "sts:AssumeRole"
#     }
#   ]
# }
# EOF
# }

# resource "aws_iam_policy" "lambda_policy" {
#   name        = "LambdaSageMakerS3Policy"
#   policy      = file("../iam/LambdaSageMakerS3Policy.json")  # Ensure JSON file contains the IAM policy above
# }

# resource "aws_iam_role_policy_attachment" "lambda_policy_attach" {
#   role       = aws_iam_role.lambda_role.name
#   policy_arn = aws_iam_policy.lambda_policy.arn
# }
