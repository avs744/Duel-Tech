# Setting Up Email Functionality on Vercel

This guide will help you configure the contact form to send emails to rishipadwal78@gmail.com when someone submits the form.

## Gmail App Password Setup

1. **Enable 2-Step Verification on your Google account**
   - Go to your Google Account: https://myaccount.google.com/
   - Select "Security" from the left navigation
   - Under "Signing in to Google," select "2-Step Verification" and follow the steps

2. **Create an App Password**
   - After enabling 2-Step Verification, go back to the Security page
   - Select "App passwords" under "Signing in to Google"
   - Select "Mail" as the app and "Other" or "Custom" as the device (name it "DuelTech Website")
   - Click "Generate"
   - Google will display a 16-character password - copy this password

## Setting Up Environment Variables on Vercel

1. **Log in to your Vercel account**
2. **Go to your project's dashboard**
3. **Navigate to "Settings" > "Environment Variables"**
4. **Add the following environment variables:**

   | Variable Name     | Value                                   |
   |-------------------|------------------------------------------|
   | `EMAIL_USER`      | Your Gmail address (for sending emails)   |
   | `EMAIL_PASSWORD`  | The app password you generated           |
   | `VERCEL_ENV`      | `production`                             |

5. **Save your environment variables**
6. **Redeploy your project**

## Testing the Email Functionality

1. Go to your deployed website
2. Navigate to the Contact page
3. Fill out the contact form and submit it
4. The message should be sent to rishipadwal78@gmail.com

## Troubleshooting

If emails aren't being sent:

1. Check your Vercel logs to see if there are any error messages
2. Verify that your environment variables are set correctly
3. Make sure your Gmail app password is valid
4. Check if your Gmail account has any security restrictions that might be blocking the emails

## Important Security Notes

- Never share your app password or commit it to your repository
- Consider using a dedicated email account for your website instead of your personal Gmail
- The app password gives access to your Gmail account, so keep it secure 