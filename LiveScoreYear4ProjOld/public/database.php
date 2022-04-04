<?php
    $dsn = 'mysql:host=localhost;dbname=liveScore';
    $username = 'A00260168';
    $password = 'sedo123O';

    //creates PDO object
    try{
        //sucess
        $db = new PDO($dsn, $username, $password);
        //echo '<p>You are connected to the database!</p>';
    } catch (PDOException $e) {
        //error
        $error_message = $e->getMessage();
        //echo "<p> An error occurred while connecting to the database: $error_message </p>";
        include('database_error.php');
        exit();
    }
    ?>