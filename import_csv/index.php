<?php






for($j = 1986; $j <= 2018; $j++){

    $manager = new MongoDB\Driver\Manager("mongodb://localhost:27017");
    $bulk = new MongoDB\Driver\BulkWrite;
    echo "Connection to database successfully";

    $arquivocsv = $j . ".csv";
    echo $j . "\n";

    $handle = file($arquivocsv);

    for ($i=1;$i<count($handle);$i++){
        
        $valori = explode(",", $handle[$i]);
        $date = date('Y-m-d', strtotime(trim($valori[1])));
        $code = trim($valori[3]);
        $price_last =  trim($valori[10]);

        $bulk->insert(['date' => $date, 'code' => $code, 'price' => $price_last]);
    }
    $manager->executeBulkWrite('yahoo.import', $bulk);
    
}