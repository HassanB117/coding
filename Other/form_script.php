
<html>
    <head><title>Thanks</title></head>
    <body>
        <h1>thank you</h1>
        <h1><a href="form.html">Go Back</a></h1>
    </body>
</html>


<?php

$email=$_POST['email'];
$name=$_POST['name'];
$data=$name.",".$email;

$file="sign in data.xlsx";

file_put_contents($file, $data . PHP_EOL, FILE_APPEND);
print ("<h1 align=center>Thank you for submitting your email address!</h1>");

?>

