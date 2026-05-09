<?php
/**
 * MobiTranz Admin Panel - PHP
 * Point d'administration simple pour MobiTranz
 */

define('API_BASE', getenv('API_BASE_URL') ?: 'http://localhost:8000');
define('API_TIMEOUT', 10);

function apiRequest($endpoint, $method = 'GET', $data = null, $token = null) {
    $ch = curl_init(API_BASE . $endpoint);
    $headers = ['Content-Type: application/json'];
    if ($token) {
        $headers[] = "Authorization: Bearer $token";
    }
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_TIMEOUT, API_TIMEOUT);
    
    if ($method === 'POST') {
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    }
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    return ['code' => $httpCode, 'data' => json_decode($response, true)];
}

$page = $_GET['page'] ?? 'dashboard';
$message = '';

// Handle login
if ($page === 'login' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $result = apiRequest('/auth/login', 'POST', [
        'phone' => $_POST['phone'],
        'password' => $_POST['password']
    ]);
    if ($result['code'] === 200) {
        setcookie('token', $result['data']['access_token'], time() + 3600, '/');
        header('Location: ?page=dashboard');
        exit;
    }
    $message = 'Erreur de connexion';
}

$token = $_COOKIE['token'] ?? null;
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MobiTranz Admin - <?= ucfirst($page) ?></title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; }
        .header { background: linear-gradient(135deg, #1A3A6C 0%, #0E2244 100%); color: white; padding: 20px 30px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 24px; }
        .nav { display: flex; gap: 10px; }
        .nav a { color: white; text-decoration: none; padding: 8px 16px; border-radius: 6px; transition: background 0.2s; }
        .nav a:hover, .nav a.active { background: rgba(255,255,255,0.2); }
        .container { max-width: 1400px; margin: 0 auto; padding: 30px; }
        .card { background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 24px; }
        .card h2 { color: #1A3A6C; margin-bottom: 16px; font-size: 20px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat { background: white; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
        .stat-value { font-size: 32px; font-weight: bold; color: #1A3A6C; }
        .stat-label { color: #666; margin-top: 8px; }
        .table { width: 100%; border-collapse: collapse; }
        .table th, .table td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        .table th { background: #f8f9fa; font-weight: 600; color: #333; }
        .badge { padding: 4px 10px; border-radius: 12px; font-size: 12px; }
        .badge-success { background: #d4edda; color: #155724; }
        .badge-warning { background: #fff3cd; color: #856404; }
        .badge-danger { background: #f8d7da; color: #721c24; }
        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; margin-bottom: 6px; font-weight: 500; }
        .form-group input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }
        .btn { padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500; }
        .btn-primary { background: #1A3A6C; color: white; }
        .btn-primary:hover { background: #0E2244; }
        .alert { padding: 16px; border-radius: 8px; margin-bottom: 20px; }
        .alert-error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚕 MobiTranz Admin</h1>
        <nav class="nav">
            <a href="?page=dashboard" class="<?= $page === 'dashboard' ? 'active' : '' ?>">Dashboard</a>
            <a href="?page=users" class="<?= $page === 'users' ? 'active' : '' ?>">Utilisateurs</a>
            <a href="?page=trips" class="<?= $page === 'trips' ? 'active' : '' ?>">Trajets</a>
            <a href="?page=payments" class="<?= $page === 'payments' ? 'active' : '' ?>">Paiements</a>
            <a href="?page=drivers" class="<?= $page === 'drivers' ? 'active' : '' ?>">Chauffeurs</a>
        </nav>
    </div>
    
    <div class="container">
        <?php if ($message): ?>
            <div class="alert alert-error"><?= htmlspecialchars($message) ?></div>
        <?php endif; ?>
        
        <?php if (!$token && $page !== 'login'): ?>
            <div class="card">
                <h2>Connexion Requise</h2>
                <p>Veuillez vous connecter pour accéder au panel admin.</p>
                <a href="?page=login" class="btn btn-primary" style="display:inline-block; margin-top:16px;">Se Connecter</a>
            </div>
        <?php elseif ($page === 'login'): ?>
            <div class="card" style="max-width: 400px; margin: 50px auto;">
                <h2>Connexion Admin</h2>
                <form method="POST">
                    <div class="form-group">
                        <label>Téléphone</label>
                        <input type="text" name="phone" required placeholder="+241 XX XX XX XX">
                    </div>
                    <div class="form-group">
                        <label>Mot de passe</label>
                        <input type="password" name="password" required>
                    </div>
                    <button type="submit" class="btn btn-primary" style="width:100%">Se Connecter</button>
                </form>
            </div>
        <?php elseif ($page === 'dashboard'): ?>
            <div class="stats">
                <div class="stat"><div class="stat-value">847</div><div class="stat-label">Taxis Actifs</div></div>
                <div class="stat"><div class="stat-value">3,240</div><div class="stat-label">Trajets/Jour</div></div>
                <div class="stat"><div class="stat-value">1.2M XAF</div><div class="stat-label">Revenus/Jour</div></div>
                <div class="stat"><div class="stat-value">42</div><div class="stat-label">Incidents</div></div>
            </div>
            <div class="card">
                <h2>Activité Récente</h2>
                <table class="table">
                    <thead>
                        <tr><th>Heure</th><th>Type</th><th>Description</th><th>Statut</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>14:32</td><td>Trajet</td><td>Owendo → Centre-ville</td><td><span class="badge badge-success">Terminé</span></td></tr>
                        <tr><td>14:15</td><td>Paiement</td><td>MoovMoney 1,500 XAF</td><td><span class="badge badge-success">Confirmé</span></td></tr>
                        <tr><td>13:58</td><td>Incident</td><td>Signalement client</td><td><span class="badge badge-warning">En cours</span></td></tr>
                        <tr><td>13:42</td><td>Trajet</td><td>Libreville → Akanda</td><td><span class="badge badge-success">Terminé</span></td></tr>
                    </tbody>
                </table>
            </div>
        <?php elseif ($page === 'users'): ?>
            <div class="card">
                <h2>Utilisateurs</h2>
                <table class="table">
                    <thead>
                        <tr><th>ID</th><th>Téléphone</th><th>Rôle</th><th>Statut</th><th>Créé</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>usr_001</td><td>+241 06 XXX XX</td><td>Client</td><td><span class="badge badge-success">Actif</span></td><td>2026-01-15</td></tr>
                        <tr><td>drv_001</td><td>+241 07 XXX XX</td><td>Chauffeur</td><td><span class="badge badge-success">Actif</span></td><td>2026-01-10</td></tr>
                        <tr><td>usr_002</td><td>+241 06 XXX XX</td><td>Client</td><td><span class="badge badge-warning">En attente</span></td><td>2026-05-01</td></tr>
                    </tbody>
                </table>
            </div>
        <?php elseif ($page === 'trips'): ?>
            <div class="card">
                <h2>Trajets</h2>
                <table class="table">
                    <thead>
                        <tr><th>ID</th><th>Client</th><th>Trajet</th><th>Montant</th><th>Statut</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>trip_001</td><td>Client A</td><td>Owendo → Centre</td><td>1,500 XAF</td><td><span class="badge badge-success">Terminé</span></td></tr>
                        <tr><td>trip_002</td><td>Client B</td><td>Akanda → Libreville</td><td>800 XAF</td><td><span class="badge badge-success">Terminé</span></td></tr>
                        <tr><td>trip_003</td><td>Client C</td><td>Port-Gentil → Aéro.</td><td>5,000 XAF</td><td><span class="badge badge-warning">En cours</span></td></tr>
                    </tbody>
                </table>
            </div>
        <?php elseif ($page === 'payments'): ?>
            <div class="card">
                <h2>Paiements</h2>
                <table class="table">
                    <thead>
                        <tr><th>ID</th><th>Méthode</th><td>Montant</th><th>Statut</th><th>Date</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>pay_001</td><td>MoovMoney</td><td>1,500 XAF</td><td><span class="badge badge-success">Succès</span></td><td>2026-05-09 14:15</td></tr>
                        <tr><td>pay_002</td><td>Airtel</td><td>800 XAF</td><td><span class="badge badge-success">Succès</span></td><td>2026-05-09 13:42</td></tr>
                        <tr><td>pay_003</td><td>MoovMoney</td><td>2,000 XAF</td><td><span class="badge badge-danger">Échec</span></td><td>2026-05-09 12:30</td></tr>
                    </tbody>
                </table>
            </div>
        <?php elseif ($page === 'drivers'): ?>
            <div class="card">
                <h2>Chauffeurs</h2>
                <table class="table">
                    <thead>
                        <tr><th>ID</th><th>Nom</th><th>Véhicule</th><th>Statut</th><th>Note</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>drv_001</td><td>Jean M.</td><td>TA-001-GA (Toyota)</td><td><span class="badge badge-success">En ligne</span></td><td>4.8 ⭐</td></tr>
                        <tr><td>drv_002</td><td>Pierre K.</td><td>TA-002-GA (Hyundai)</td><td><span class="badge badge-success">En ligne</span></td><td>4.9 ⭐</td></tr>
                        <tr><td>drv_003</td><td>Marie L.</td><td>TA-003-GA (Kia)</td><td><span class="badge badge-warning">Hors ligne</span></td><td>4.7 ⭐</td></tr>
                    </tbody>
                </table>
            </div>
        <?php endif; ?>
    </div>
</body>
</html>