<?php
class db
{
    static function connect(){
        $db_ip          = '';
        $db_user        = '';
        $db_password    = '';
        $db_select      = '';
        $db_charset     = '';
        $DSN="mysql:host=$db_ip;dbname=$db_select;charset=$db_charset";
        try{
            $db=new PDO($DSN,$db_user,$db_password);
            $db->setAttribute(PDO::ATTR_ERRMODE,PDO::ERRMODE_EXCEPTION);
        }
        catch(PDOException $e){
            echo "連接失敗 ： " . $e->getMessage();
        }
        return $db;
    }
}

?>