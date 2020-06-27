<?php
    require('db.php');

    $sql = 'SELECT * FROM `problem` WHERE 1 ORDER BY RAND() LIMIT 1';
    $result = db::connect()->prepare($sql);
    $result->execute();

    $data = $result->fetch();

    $ans = json_encode([
        'id' => $data[0],
        'problem' => $data[1]
    ]);
    echo $ans;
?>