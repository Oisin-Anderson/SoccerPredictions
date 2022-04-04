<?php
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Factory\AppFactory;

require __DIR__ . '/../vendor/autoload.php';

$app = AppFactory::create();

$app->addBodyParsingMiddleware(); // <<<---- here
$app->setBasePath("/LiveScoreYear4Proj/public");

// Get all teams
$app->get('/standings', function (Request $request, Response $response, $args) {

    require_once('database.php');
  // Get all teams
  $query = 'SELECT * FROM standings order by position';
  $prem = $db->query($query)->fetchAll(PDO::FETCH_ASSOC);
  //$prem contain the result set    
    $response->getBody()->write(json_encode($prem));
    return $response->withHeader('Content-Type', 'application/json');
});

$app->get('/players', function (Request $request, Response $response, $args) {

  require_once('database.php');
// Get all films
$query = 'SELECT * FROM players';
$tScorers = $db->query($query)->fetchAll(PDO::FETCH_ASSOC);
//$films contain the result set    
  $response->getBody()->write(json_encode($tScorers));
  return $response->withHeader('Content-Type', 'application/json');
});

// Update new film using x-www-form-urlencoded content type
$app->put('/standings/{id}', function (Request $request, Response $response, $args) {

  require_once('database.php');
  // Get film details
  $formData = (array)$request->getParsedBody();

  $id = $args['id'];
  $position = $formData['position'];
  $name = $formData['name'];
  $played = $formData['played'];
  $win = $formData['win'];
  $draw = $formData['draw'];
  $loss = $formData['loss'];
  $gfor = $formData['gfor'];
  $gagainst = $formData['gagainst'];
  $gdiff = $formData['gdiff'];
  $points = $formData['points'];

  $query = "UPDATE standings set position = '$position', name = '$name', played = '$played', win = '$win', draw = '$draw', loss = '$loss', gfor = '$gfor', gagainst = '$gagainst', gdiff = '$gdiff', points = '$points' WHERE ID = '$id'";
  $insert_count = $db->exec($query);

  //$films contain the result set    
  $response->getBody()->write(json_encode($insert_count));
  return $response->withHeader('Content-Type', 'application/json');
});

// Update new film using x-www-form-urlencoded content type
$app->put('/players/{id}', function (Request $request, Response $response, $args) {

  require_once('database.php');
  // Get film details
  $formData = (array)$request->getParsedBody();

  $id = $args['id'];
  $player = $formData['player'];
  $position = $formData['position'];
  $played = $formData['played'];
  $goals = $formData['goals'];

  $query = "UPDATE players set  player = '$player', position = '$position', played = '$played', goals = '$goals' WHERE id = '$id'";
  $insert_count = $db->exec($query);

  //$films contain the result set    
  $response->getBody()->write(json_encode($insert_count));
  return $response->withHeader('Content-Type', 'application/json');
});

$app->post('/prem', function (Request $request, Response $response, $args) {

  require_once('database.php');
  // Get film details
  $formData = (array)$request->getParsedBody();

    $id = $formData['id'];
    $name = $formData['player'];
    $position = $formData['position'];
    $played = $formData['played'];
    $goals = $formData['goals'];

    $query = "INSERT INTO tScorers (id, player, position, played, goals) VALUES ('$id', '$name', '$position', '$played', '$goals')";
    $insert_count = $db->exec($query);
 
  //$films contain the result set    
  $response->getBody()->write(json_encode($insert_count));
  return $response->withHeader('Content-Type', 'application/json');
});

try {
    $app->run();     
} catch (Exception $e) {    
  // We display a error message
  die( json_encode(array("status" => "failed", "message" => "This action is not allowed"))); 
}