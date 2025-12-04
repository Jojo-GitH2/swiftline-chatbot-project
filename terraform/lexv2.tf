resource "aws_cloudformation_stack" "lex_bot_stack" {
  name          = "${local.name-prefix}-lex-bot-stack"
  template_body = file("${path.module}/aws_cfn_template.yml")
  capabilities  = ["CAPABILITY_IAM"]

  parameters = {
    BotName              = "SwiftLineBot"
    LexRoleArn           = aws_iam_role.lex_bot_role.arn
    LambdaFulfillmentArn = aws_lambda_function.lex_fulfillment.arn
    BotAliasName         = "LiveBotAlias"
    
    # === PASSING TAGS TO CFN ===
    AssessmentTag = "SolutionsEngineer-candidate-jonah"
    ProjectTag    = "Swiftline"
    CreatedByTag  = "terraform"

    LexLogGroupArn = aws_cloudwatch_log_group.lex_logs.arn
    
  }
  

  # depends_on = [
  #   aws_iam_role.lex_bot_role,
  #   aws_lambda_function.lex_fulfillment
  # ]
}