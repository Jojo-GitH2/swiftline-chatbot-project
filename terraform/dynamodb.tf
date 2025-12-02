resource "aws_dynamodb_table" "orders" {
  name         = "${local.name-prefix}-orders"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "trackingId"

  attribute {
    name = "trackingId"
    type = "S"
  }
}

resource "aws_dynamodb_table_item" "sample_order" {
  table_name = aws_dynamodb_table.orders.name
  hash_key   = aws_dynamodb_table.orders.hash_key

  item = jsonencode({
    trackingId = { S = "SWL-2024-AIR-001234" }
    orderDate  = { S = "2024-11-15" }
    orderDetails = {
      M = {
        items = {
          L = [
            {
              M = {
                name     = { S = "Electronics Package" }
                quantity = { N = "2" }
                vendor   = { S = "TechCorp" }
              }
            }
          ]
        }
      }
    }
    customer = {
      M = {
        name  = { S = "John Doe" }
        phone = { S = "+1-555-0123" }
        email = { S = "john.doe@example.com" }
      }
    }
    delivery = {
      M = {
        method        = { S = "Air" }
        estimatedDate = { S = "2024-11-20" }
        carrier       = { S = "SwiftAir Express" }
        status        = { S = "In Transit" }
      }
    }
  })
}