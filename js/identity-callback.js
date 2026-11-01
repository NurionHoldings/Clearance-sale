// Keep Identity confirmation, recovery and invitation callbacks on the dedicated partner page.
if(/^#(?:access_token|confirmation_token|invite_token|recovery_token|email_change_token)=/.test(location.hash)){
 location.replace(new URL('operations.html'+location.hash,location.href));
}
