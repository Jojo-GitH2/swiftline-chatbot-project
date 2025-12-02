

resource "aws_lexv2models_bot" "swiftline_bot" {
  name        = "SwiftLineBot"
  description = "Bot handling order tracking inquiries for Swiftline"
  data_privacy {
    child_directed = false
  }

  idle_session_ttl_in_seconds = 60
  role_arn                    = aws_iam_role.lex_bot_role.arn
  type                        = "Bot"


}


resource "aws_lexv2models_bot_locale" "en_us" {
  bot_id                           = aws_lexv2models_bot.swiftline_bot.id
  bot_version                      = "DRAFT"
  locale_id                        = "en_US"
  description                      = "English (US) locale for SwiftLineBot"
  n_lu_intent_confidence_threshold = 0.70

}


# resource "aws_lexv2models_slot_type" "tracking_id_type" {
#   bot_id = aws_lexv2models_bot.swiftline_bot.id
#   bot_version = aws_lexv2models_bot_locale.en_us.bot_version
#   name = "TrackingIDType"
#   locale_id = aws_lexv2models_bot_locale.en_us.locale_id

#   slot_type_values {
#     sample_value {
#       value =  "SWL-2024-AIR-001234"
#     }
#   }

#   value_selection_setting {
#     resolution_strategy = "OriginalValue"
#     advanced_recognition_setting {
#       audio_recognition_strategy = "UseSlotValuesAsCustomVocabulary"
#     }
#   }

#   depends_on = [ aws_lexv2models_bot_locale.en_us ]
# }


resource "aws_lexv2models_intent" "get_order_status" {
  bot_id      = aws_lexv2models_bot.swiftline_bot.id
  bot_version = aws_lexv2models_bot_locale.en_us.bot_version
  locale_id   = aws_lexv2models_bot_locale.en_us.locale_id
  name        = "GetOrderStatus"
  description = "Intent to retrieve order details by tracking ID"

  sample_utterance {
    utterance = "What is the status of my order {TrackingID}"
  }

  sample_utterance {
    utterance = "Track my order with ID {TrackingID}"
  }

  sample_utterance {
    utterance = "Where is my order {TrackingID}"
  }

  sample_utterance {
    utterance = "Track order {TrackingID}"
  }

  sample_utterance {
    utterance = "Order status for {TrackingID}"
  }

  fulfillment_code_hook {
    enabled = true
    post_fulfillment_status_specification {
      success_response {
        allow_interrupt = false
        # The API requires a message group, even if the Lambda provides the response.
        message_group {
          message {
            plain_text_message {
              value = "OK"
            }
          }
        }
      }
    }
    fulfillment_updates_specification {
      active = false
    }
  }

}

resource "aws_lexv2models_slot" "tracking_id" {
  bot_id      = aws_lexv2models_bot.swiftline_bot.id
  bot_version = aws_lexv2models_bot_locale.en_us.bot_version
  locale_id   = aws_lexv2models_bot_locale.en_us.locale_id
  intent_id   = aws_lexv2models_intent.get_order_status.intent_id
  name        = "TrackingID"

  slot_type_id = "AMAZON.AlphaNumeric"
  value_elicitation_setting {
    slot_constraint = "Required"
    prompt_specification {
      max_retries                = 2
      allow_interrupt            = true
      message_selection_strategy = "Random"
      message_group {
        message {
          plain_text_message {
            value = "Please provide your order tracking ID."
          }
        }
      }
    }
  }

  lifecycle {
    ignore_changes = [
      value_elicitation_setting
    ]
  }

}

resource "aws_lex_bot_alias" "live_alias" {
  bot_name = aws_lexv2models_bot.swiftline_bot.name
  bot_version = "DRAFT"
  name = "${local.name-prefix}-lex-bot-alias"
}

# resource "aws_lex_bot_alias" "live_alias" {
#   name   = "live"
#   bot_id = aws_lexv2models_bot.swiftline_bot.id

#   bot_version = "DRAFT" # For testing, we point the alias to the DRAFT version

#   bot_alias_locale_settings {
#     locale_id = aws_lexv2models_bot_locale.en_us.locale_id
#     enabled   = true
#     code_hook_specification {
#       lambda_code_hook {
#         code_hook_interface_version = "1.0"
#         lambda_arn                  = aws_lambda_function.lex_fulfillment.arn
#       }
#     }
#   }

#   conversation_log_settings {
#     cloudwatch_log_group_arn = aws_cloudwatch_log_group.lex_logs.arn
#     log_destination {
#       cloudwatch_logs_log_destination {
#         cloudwatch_log_group_arn = aws_cloudwatch_log_group.lex_logs.arn
#       }
#     }
#   }

# }

# resource "aws_lexv2models_bot_version" "v1" {
#   bot_id = aws_lexv2models_bot.swiftline_bot.id
#   locale_specification = {
#     en-US = {
#       source_bot_version = "DRAFT"
#     }
#   }

#   depends_on = [aws_lexv2models_intent.get_order_status, aws_lexv2models_slot.tracking_id]
# }

# resource "awscc_lex" "name" {

# }