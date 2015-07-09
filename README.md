# The SSO for P2PU entities

It only covers signin for discourse for now.

### How to change settings in discourse?

Under Settings > Login

* check the enable sso checkbox
* set sso url to: `http://host_of_sso/discourse/login/`
* set the sso secret (this is set in the main sso app)

For the seamless logout we need to set the logout redirect in the discourse

Under Settings > Users

* set the logout redirect to `http://host_of_sso/accounts/logout/`