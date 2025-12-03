data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "../src/lex_fulfillment.py"
  output_path = "../src/lex_fulfillment.zip"
}

resource "aws_lambda_function" "lex_fulfillment" {
  function_name = "${local.name-prefix}-lex-fulfillment"
  role          = aws_iam_role.lambda_exec.arn

  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  handler = "lex_fulfillment.lambda_handler"
  runtime = "python3.12"
  timeout = 10

  environment {
    variables = {
      ORDERS_TABLE = aws_dynamodb_table.orders.name
    }
  }
}

resource "aws_lambda_permission" "lex_invoke" {
  statement_id  = "AllowLexToInvokeLambda"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lex_fulfillment.function_name
  principal     = "lexv2.amazonaws.com"
}