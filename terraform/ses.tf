# Amazon SES — outbound mail transport (docs/specs/SPEC_outbound_mail.md §5).
#
# Scope is the send path only, enough for the /api/test-email smoke test. Not created
# here, and all required before this is a mail transport rather than a test rig:
#
#   §13  delivery event topic and the ingestion endpoint's shared secret
#   §22  DKIM, custom envelope sender (MAIL FROM) and DMARC records
#   §20.2 a configuration set with open and click tracking explicitly disabled
#   §14  the application's own suppression list
#
# Because none of the above exists, §11's capability reporting would report that this
# transport does not report delivery. It does not yet.
#
# The sender is verified as an *e-mail address* identity, not a domain identity: the
# DNS for dxc.com is not managed by this configuration, so the domain cannot be DKIM
# signed from here. Creating this resource makes SES mail a verification link to
# catalystx-support@dxc.com; the identity remains unverified — and every send fails —
# until someone with access to that mailbox opens it. Terraform will report the
# resource as created regardless, so check the ses_identity_verified output.
#
# An address identity also means SPF and DKIM align to amazonses.com rather than to
# dxc.com. Deliverable enough for a test to an internal recipient; not deliverable
# enough for §22, and not a basis for sending authentication mail to executives.

resource "aws_sesv2_email_identity" "sender" {
  email_identity = var.mail_from_address

  tags = local.tags
}

# A sandboxed SES account may only send *to* verified identities, so the test
# recipients are verified too. Each one gets its own verification mail that its owner
# must open. Test scaffolding: once the account leaves the sandbox these serve no
# purpose, and a real recipient is never a verified identity.
resource "aws_sesv2_email_identity" "test_recipient" {
  for_each = toset(var.test_recipient_addresses)

  email_identity = each.value

  tags = local.tags
}

# §20.4: authorization to send is scoped to the sending identity, so a workload
# compromised through another path cannot send as an arbitrary address. Scoped twice —
# by resource, and by the From address itself.
#
# In sandbox mode, we must verify both sender and test recipients as SES identities,
# so the Resource includes both. Once the account leaves the sandbox, remove
# aws_sesv2_email_identity.test_recipient and revert Resource to sender.arn only.
resource "aws_iam_role_policy" "task_role_ses" {
  name = "${local.app_name}-task-ses"
  role = aws_iam_role.task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "ses:SendEmail"
      ]
      Resource = concat(
        [aws_sesv2_email_identity.sender.arn],
        [for identity in aws_sesv2_email_identity.test_recipient : identity.arn]
      )
      Condition = {
        StringEquals = {
          "ses:FromAddress" = var.mail_from_address
        }
      }
    }]
  })
}
