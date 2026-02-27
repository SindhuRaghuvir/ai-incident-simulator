# Account and Login Help

## Password and Login Issues

### How do I reset my password?
1. Go to dashboard.stratifylabs.io and click "Sign In"
2. Click "Forgot password?" below the login form
3. Enter the email address associated with your account
4. Check your inbox for a password reset link — it arrives within a few minutes
5. Click the link and set a new password

The reset link expires after 1 hour. If it expires, request a new one by repeating the steps above.

### I'm not receiving the password reset email
First, check your spam or junk folder. If it's not there:
- Make sure you're using the email address associated with your Stratify Labs account
- Try adding no-reply@stratifylabs.io to your contacts and request again
- If your company uses email filtering, ask your IT admin to allowlist mail from stratifylabs.io

Still nothing? Contact support@stratifylabs.io and we'll reset it for you manually.

### My account is locked — what do I do?
Accounts are temporarily locked after several failed login attempts. To unlock your account:

1. Wait 15 minutes and try again — the lockout lifts automatically
2. If you're still locked out, click "Forgot password?" to reset your password, which also unlocks the account
3. If neither works, contact support@stratifylabs.io and we'll unlock your account right away

### I can't log in with SSO — what should I check?
SSO login issues are usually caused by one of these:

1. **SSO not configured** — SSO is available on Professional and Enterprise plans. If your plan doesn't include it, you'll need to use email/password login.
2. **Identity provider misconfiguration** — Your IT admin may need to verify the SAML/OIDC setup in your IdP settings.
3. **Account not provisioned** — Your email address may not be in the IdP user directory. Ask your admin to add you.
4. **SSO enforced on your org** — If your org has enforced SSO and disabled password login, you must log in through your company's identity provider.

If you're the org Owner and have locked yourself out of SSO, contact support@stratifylabs.io — we have a recovery path that doesn't require going through your IdP.

---

## Multi-Factor Authentication (MFA)

### How do I set up MFA?
1. Go to **Settings > Security > Authentication**
2. Click "Enable MFA"
3. Choose your preferred method: authenticator app (Google Authenticator, Authy), SMS, or hardware key (YubiKey, FIDO2)
4. Follow the setup instructions and enter the verification code to confirm

Authenticator apps and hardware keys are more secure than SMS and recommended for Owners and Admins.

### I lost access to my MFA device — how do I recover?
If you set up backup codes when you enabled MFA, use one of those to log in:
1. On the MFA prompt, click "Use a recovery code"
2. Enter one of your backup codes
3. Once logged in, go to **Settings > Security** and reconfigure MFA with your new device

**No backup codes?** Contact support@stratifylabs.io from the email address on your account. We'll verify your identity and help you regain access. This process may take up to 1 business day for security reasons.

### My organization requires MFA but I can't complete setup
If your org admin has enforced MFA, you'll be prompted to set it up on your next login before you can access anything else. If you're stuck in the MFA setup flow, contact support@stratifylabs.io with your account email and we'll assist.

---

## Account Settings

### How do I change my email address?
1. Log in and go to **Settings > Profile**
2. Click "Change Email"
3. Enter your new email address
4. A verification link will be sent to the new address — click it to confirm the change

Your old email address continues to work until you verify the new one.

### How do I change my account name or display name?
Go to **Settings > Profile** and update your name. Changes take effect immediately.

### How do I delete my account?
Before deleting your account, note that:
- All your data, API keys, and settings will be permanently removed
- If you're the Organization Owner, you must transfer ownership to another member first (or delete the entire organization)
- Deletion cannot be undone

To delete your account, go to **Settings > Profile > Delete Account**. You'll be asked to confirm with your password.

If you're having trouble deleting your account, or if you're the last member of an organization and want to close everything, contact support@stratifylabs.io and we'll walk you through it.

---

## Team Invitations

### I can't accept my team invitation — what should I do?
Invitation links expire after **7 days**. If your link has expired:
1. Ask your team's Owner or Admin to resend the invitation from **Settings > Team**
2. Check that you're opening the link in the same browser where you're not already logged in with a different account

If the link is still fresh and not working:
- Try opening it in an incognito/private browser window
- Make sure the email address on the invitation matches the one you're trying to sign up with

If you're still blocked, forward the invitation email to support@stratifylabs.io and we'll sort it out.

### I sent a team invitation but the person never received it
Ask them to check their spam folder for an email from no-reply@stratifylabs.io. If it's not there, you can resend the invitation from **Settings > Team** — click the three-dot menu next to the pending invite and select "Resend."

### How do I remove a team member?
Go to **Settings > Team**, find the member you want to remove, click the three-dot menu, and select "Remove." Their access is revoked immediately and their personal API keys are deactivated. Organization-level API keys are not affected.

---

## Still Need Help?

If you're locked out and can't access your settings at all, email support@stratifylabs.io directly. Include:
- The email address on your account
- A brief description of what you're experiencing
- Whether your organization uses SSO

We'll get back to you as quickly as possible.
