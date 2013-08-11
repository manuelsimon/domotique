mySqlUser="root"
mySqlPwd="password"
mySqlDatabase="test"
# mysql --user=$mySqlUser --password=$mySqlUserPwd --database=$mySqlDatabase < createDatabase.sql
mysql --database=$mySqlDatabase < createDatabase.sql