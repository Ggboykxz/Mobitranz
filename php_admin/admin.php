<?php
/**
 * MobiTranz Desktop Admin - Application PHP
 * Interface d'administration complète style Windows 11 Fluent
 */

session_start();

define('API_BASE', getenv('API_BASE_URL') ?: 'http://localhost:8000');
define('APP_SECRET', 'mobitranz-admin-2026');

$page = $_GET['page'] ?? 'dashboard';
$user = $_SESSION['user'] ?? null;

// Route API
function apiRequest($endpoint, $method = 'GET', $data = null, $token = null) {
    $ch = curl_init(API_BASE . $endpoint);
    $headers = ['Content-Type: application/json', 'Accept: application/json'];
    if ($token) $headers[] = "Authorization: Bearer $token";
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
    if ($method === 'POST') {
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    }
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    return $httpCode >= 200 && $httpCode < 300 ? json_decode($response, true) : null;
}

// Login handler
if ($page === 'login' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';
    
    if ($username === 'admin' && $password === 'admin123') {
        $_SESSION['user'] = ['username' => 'admin', 'role' => 'admin'];
        $_SESSION['token'] = 'demo-token-' . time();
        header('Location: ?page=dashboard');
        exit;
    }
    $error = 'Identifiants invalides';
}

if ($page === 'logout') {
    session_destroy();
    header('Location: ?page=login');
    exit;
}

// Demo data
$stats = [
    'trips_today' => 342,
    'revenue_today' => 1250000,
    'active_drivers' => 847,
    'active_vehicles' => 892,
    'incidents' => 12,
    'users_total' => 4523
];

$recent_trips = [
    ['id' => 'TRP-001', 'client' => 'Client A', 'route' => 'Owendo → Centre', 'amount' => 1500, 'status' => 'completed'],
    ['id' => 'TRP-002', 'client' => 'Client B', 'route' => 'Akanda → Libreville', 'amount' => 800, 'status' => 'completed'],
    ['id' => 'TRP-003', 'client' => 'Client C', 'route' => 'Port-Gentil → Aéroport', 'amount' => 5000, 'status' => 'pending'],
    ['id' => 'TRP-004', 'client' => 'Client D', 'route' => 'Libreville → Owendo', 'amount' => 1200, 'status' => 'completed'],
    ['id' => 'TRP-005', 'client' => 'Client E', 'route' => 'Ntoum → Libreville', 'amount' => 600, 'status' => 'cancelled'],
];

$drivers = [
    ['id' => 'DRV-001', 'name' => 'Jean M.', 'phone' => '+241 06 XXX XX', 'vehicle' => 'TA-001-GA', 'status' => 'online', 'rating' => 4.8],
    ['id' => 'DRV-002', 'name' => 'Pierre K.', 'phone' => '+241 07 XXX XX', 'vehicle' => 'TA-002-GA', 'status' => 'online', 'rating' => 4.9],
    ['id' => 'DRV-003', 'name' => 'Marie L.', 'phone' => '+241 06 XXX XX', 'vehicle' => 'TA-003-GA', 'status' => 'offline', 'rating' => 4.7],
];

$payments = [
    ['id' => 'PAY-001', 'method' => 'MoovMoney', 'amount' => 1500, 'status' => 'success', 'time' => '14:32'],
    ['id' => 'PAY-002', 'method' => 'Airtel', 'amount' => 800, 'status' => 'success', 'time' => '13:45'],
    ['id' => 'PAY-003', 'method' => 'MoovMoney', 'amount' => 2500, 'status' => 'pending', 'time' => '13:15'],
    ['id' => 'PAY-004', 'method' => 'Airtel', 'amount' => 1000, 'status' => 'failed', 'time' => '12:30'],
];

$incidents = [
    ['id' => 'INC-001', 'type' => 'Signalement client', 'trip' => 'TRP-002', 'status' => 'open', 'time' => '14:20'],
    ['id' => 'INC-002', 'type' => 'Accident', 'trip' => 'TRP-001', 'status' => 'resolved', 'time' => '10:15'],
];
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MobiTranz Admin - <?= ucfirst($page) ?></title>
    <style>
        :root {
            --primary: #1A3A6C;
            --primary-dark: #0E2244;
            --accent: #009E60;
            --warning: #FCD116;
            --danger: #E53E3E;
            --bg: #F3F4F6;
            --surface: #FFFFFF;
            --text: #1F2937;
            --text-secondary: #6B7280;
            --border: #E5E7EB;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', -apple-system, sans-serif; background: var(--bg); color: var(--text); }
        
        /* Layout */
        .app { display: flex; min-height: 100vh; }
        .sidebar { width: 260px; background: linear-gradient(180deg, var(--primary) 0%, var(--primary-dark) 100%); color: white; padding: 20px 0; position: fixed; height: 100vh; }
        .sidebar-logo { padding: 0 20px 30px; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px; }
        .sidebar-logo h1 { font-size: 22px; font-weight: 600; display: flex; align-items: center; gap: 10px; }
        .sidebar-logo span { font-size: 28px; }
        
        .nav-item { display: flex; align-items: center; gap: 12px; padding: 12px 20px; color: rgba(255,255,255,0.8); text-decoration: none; transition: all 0.2s; cursor: pointer; }
        .nav-item:hover, .nav-item.active { background: rgba(255,255,255,0.1); color: white; }
        .nav-item span.icon { font-size: 18px; }
        
        .main { flex: 1; margin-left: 260px; padding: 24px; }
        
        /* Header */
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
        .header h2 { font-size: 28px; font-weight: 600; color: var(--primary); }
        .header-actions { display: flex; gap: 12px; align-items: center; }
        .user-menu { display: flex; align-items: center; gap: 8px; padding: 8px 16px; background: var(--surface); border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        
        /* Cards */
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 24px; }
        .stat-card { background: var(--surface); border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .stat-card .label { font-size: 13px; color: var(--text-secondary); margin-bottom: 8px; }
        .stat-card .value { font-size: 32px; font-weight: 700; color: var(--primary); }
        .stat-card .trend { font-size: 12px; color: var(--accent); margin-top: 4px; }
        
        /* Tables */
        .card { background: var(--surface); border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 24px; }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
        .card-title { font-size: 18px; font-weight: 600; color: var(--primary); }
        
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px 16px; text-align: left; border-bottom: 1px solid var(--border); }
        th { font-size: 12px; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; background: #F9FAFB; }
        tr:hover { background: #F9FAFB; }
        
        /* Badges */
        .badge { display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500; }
        .badge-success { background: #D1FAE5; color: #065F46; }
        .badge-warning { background: #FEF3C7; color: #92400E; }
        .badge-danger { background: #FEE2E2; color: #991B1B; }
        .badge-info { background: #DBEAFE; color: #1E40AF; }
        
        /* Buttons */
        .btn { padding: 10px 20px; border: none; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s; text-decoration: none; display: inline-block; }
        .btn-primary { background: var(--primary); color: white; }
        .btn-primary:hover { background: var(--primary-dark); }
        .btn-secondary { background: var(--surface); color: var(--text); border: 1px solid var(--border); }
        .btn-accent { background: var(--accent); color: white; }
        
        /* Forms */
        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; margin-bottom: 6px; font-weight: 500; }
        .form-group input { width: 100%; padding: 12px; border: 1px solid var(--border); border-radius: 8px; font-size: 14px; }
        .form-group input:focus { outline: none; border-color: var(--primary); }
        
        /* Login Page */
        .login-page { display: flex; align-items: center; justify-content: center; min-height: 100vh; background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%); }
        .login-box { background: white; border-radius: 16px; padding: 40px; width: 400px; box-shadow: 0 20px 40px rgba(0,0,0,0.2); }
        .login-box h1 { text-align: center; margin-bottom: 8px; color: var(--primary); }
        .login-box p { text-align: center; color: var(--text-secondary); margin-bottom: 32px; }
        
        /* Charts placeholder */
        .chart { height: 200px; background: linear-gradient(90deg, #E5E7EB 0%, #D1D5DB 100%); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: var(--text-secondary); }
        
        /* Time */
        .time { font-size: 12px; color: var(--text-secondary); }
    </style>
</head>
<body>
<?php if (!$user && $page !== 'login'): ?>
    <div class="login-page">
        <div class="login-box">
            <h1>🚕 MobiTranz</h1>
            <p>Administration</p>
            <?php if (isset($error)): ?>
                <div class="badge badge-danger" style="margin-bottom: 16px; display: block;"><?= $error ?></div>
            <?php endif; ?>
            <form method="POST">
                <div class="form-group">
                    <label>Nom d'utilisateur</label>
                    <input type="text" name="username" required placeholder="admin">
                </div>
                <div class="form-group">
                    <label>Mot de passe</label>
                    <input type="password" name="password" required placeholder="••••••••">
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%;">Se connecter</button>
            </form>
            <p style="margin-top: 16px; font-size: 12;">Demo: admin / admin123</p>
        </div>
    </div>
<?php elseif ($page === 'login'): ?>
    <?php header('Location: ?page=dashboard'); exit; ?>
<?php else: ?>
    <div class="app">
        <aside class="sidebar">
            <div class="sidebar-logo">
                <h1><span>🚕</span> MobiTranz</h1>
            </div>
            <nav>
                <a href="?page=dashboard" class="nav-item <?= $page === 'dashboard' ? 'active' : '' ?>">
                    <span class="icon">📊</span> Dashboard
                </a>
                <a href="?page=trips" class="nav-item <?= $page === 'trips' ? 'active' : '' ?>">
                    <span class="icon">🚗</span> Trajets
                </a>
                <a href="?page=drivers" class="nav-item <?= $page === 'drivers' ? 'active' : '' ?>">
                    <span class="icon">👨‍💼</span> Chauffeurs
                </a>
                <a href="?page=vehicles" class="nav-item <?= $page === 'vehicles' ? 'active' : '' ?>">
                    <span class="icon">🚙</span> Véhicules
                </a>
                <a href="?page=payments" class="nav-item <?= $page === 'payments' ? 'active' : '' ?>">
                    <span class="icon">💳</span> Paiements
                </a>
                <a href="?page=incidents" class="nav-item <?= $page === 'incidents' ? 'active' : '' ?>">
                    <span class="icon">⚠️</span> Incidents
                </a>
                <a href="?page=users" class="nav-item <?= $page === 'users' ? 'active' : '' ?>">
                    <span class="icon">👥</span> Utilisateurs
                </a>
                <a href="?page=analytics" class="nav-item <?= $page === 'analytics' ? 'active' : '' ?>">
                    <span class="icon">📈</span> Analytics
                </a>
                <a href="?page=settings" class="nav-item <?= $page === 'settings' ? 'active' : '' ?>">
                    <span class="icon">⚙️</span> Paramètres
                </a>
                <a href="?page=logout" class="nav-item">
                    <span class="icon">🚪</span> Déconnexion
                </a>
            </nav>
        </aside>
        
        <main class="main">
            <header class="header">
                <h2><?= ucfirst($page) ?></h2>
                <div class="header-actions">
                    <span class="time"><?= date('d/m/Y H:i') ?></span>
                    <div class="user-menu">
                        <span>👤</span>
                        <span><?= $user['username'] ?></span>
                    </div>
                </div>
            </header>
            
            <?php if ($page === 'dashboard'): ?>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="label">Trajets aujourd'hui</div>
                        <div class="value"><?= $stats['trips_today'] ?></div>
                        <div class="trend">↑ 12% vs hier</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Revenus aujourd'hui</div>
                        <div class="value"><?= number_format($stats['revenue_today'], 0, ',', ' ') ?> XAF</div>
                        <div class="trend">↑ 8% vs hier</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Chauffeurs en ligne</div>
                        <div class="value"><?= $stats['active_drivers'] ?></div>
                        <div class="trend"><?= $stats['active_vehicles'] ?> véhicules</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Incidents ouverts</div>
                        <div class="value"><?= $stats['incidents'] ?></div>
                        <div class="trend">↓ 3 vs semaine dernière</div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Trajets Récents</div>
                        <a href="?page=trips" class="btn btn-secondary">Voir tout</a>
                    </div>
                    <table>
                        <thead>
                            <tr><th>ID</th><th>Client</th><th>Trajet</th><th>Montant</th><th>Statut</th></tr>
                        </thead>
                        <tbody>
                            <?php foreach ($recent_trips as $trip): ?>
                            <tr>
                                <td><?= $trip['id'] ?></td>
                                <td><?= $trip['client'] ?></td>
                                <td><?= $trip['route'] ?></td>
                                <td><?= number_format($trip['amount'], 0, ',', ' ') ?> XAF</td>
                                <td>
                                    <?php if ($trip['status'] === 'completed'): ?>
                                        <span class="badge badge-success">Terminé</span>
                                    <?php elseif ($trip['status'] === 'pending'): ?>
                                        <span class="badge badge-warning">En cours</span>
                                    <?php else: ?>
                                        <span class="badge badge-danger">Annulé</span>
                                    <?php endif; ?>
                                </td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
                    <div class="card">
                        <div class="card-title">Activité du Jour</div>
                        <div class="chart">Graphique d'activité en temps réel</div>
                    </div>
                    <div class="card">
                        <div class="card-title">Répartition des Paiements</div>
                        <div class="chart">Pie chart MoovMoney / Airtel</div>
                    </div>
                </div>
            <?php endif; ?>
            
            <?php if ($page === 'trips'): ?>
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Tous les Trajets</div>
                        <button class="btn btn-primary">+ Nouveau trajet</button>
                    </div>
                    <table>
                        <thead>
                            <tr><th>ID</th><th>Client</th><th>Trajet</th><th>Montant</th><th>Statut</th><th>Actions</th></tr>
                        </thead>
                        <tbody>
                            <?php foreach ($recent_trips as $trip): ?>
                            <tr>
                                <td><?= $trip['id'] ?></td>
                                <td><?= $trip['client'] ?></td>
                                <td><?= $trip['route'] ?></td>
                                <td><?= number_format($trip['amount'], 0, ',', ' ') ?> XAF</td>
                                <td>
                                    <?php if ($trip['status'] === 'completed'): ?>
                                        <span class="badge badge-success">Terminé</span>
                                    <?php elseif ($trip['status'] === 'pending'): ?>
                                        <span class="badge badge-warning">En cours</span>
                                    <?php else: ?>
                                        <span class="badge badge-danger">Annulé</span>
                                    <?php endif; ?>
                                </td>
                                <td><a href="#" class="btn btn-secondary" style="padding: 4px 12px; font-size: 12px;">Détails</a></td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            <?php endif; ?>
            
            <?php if ($page === 'drivers'): ?>
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Chauffeurs</div>
                        <button class="btn btn-primary">+ Ajouter chauffeur</button>
                    </div>
                    <table>
                        <thead>
                            <tr><th>ID</th><th>Nom</th><th>Téléphone</th><th>Véhicule</th><th>Statut</th><th>Note</th></tr>
                        </thead>
                        <tbody>
                            <?php foreach ($drivers as $driver): ?>
                            <tr>
                                <td><?= $driver['id'] ?></td>
                                <td><?= $driver['name'] ?></td>
                                <td><?= $driver['phone'] ?></td>
                                <td><?= $driver['vehicle'] ?></td>
                                <td>
                                    <span class="badge <?= $driver['status'] === 'online' ? 'badge-success' : 'badge-warning' ?>">
                                        <?= $driver['status'] === 'online' ? 'En ligne' : 'Hors ligne' ?>
                                    </span>
                                </td>
                                <td><?= $driver['rating'] ?> ⭐</td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            <?php endif; ?>
            
            <?php if ($page === 'payments'): ?>
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Historique des Paiements</div>
                    </div>
                    <table>
                        <thead>
                            <tr><th>ID</th><th>Méthode</th><th>Montant</th><th>Statut</th><th>Heure</th></tr>
                        </thead>
                        <tbody>
                            <?php foreach ($payments as $payment): ?>
                            <tr>
                                <td><?= $payment['id'] ?></td>
                                <td><?= $payment['method'] ?></td>
                                <td><?= number_format($payment['amount'], 0, ',', ' ') ?> XAF</td>
                                <td>
                                    <?php if ($payment['status'] === 'success'): ?>
                                        <span class="badge badge-success">Succès</span>
                                    <?php elseif ($payment['status'] === 'pending'): ?>
                                        <span class="badge badge-warning">En attente</span>
                                    <?php else: ?>
                                        <span class="badge badge-danger">Échec</span>
                                    <?php endif; ?>
                                </td>
                                <td><?= $payment['time'] ?></td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            <?php endif; ?>
            
            <?php if ($page === 'incidents'): ?>
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Incidents</div>
                        <button class="btn btn-primary" style="background: var(--danger);">+ Signaler</button>
                    </div>
                    <table>
                        <thead>
                            <tr><th>ID</th><th>Type</th><th>Trajet</th><th>Statut</th><th>Heure</th></tr>
                        </thead>
                        <tbody>
                            <?php foreach ($incidents as $incident): ?>
                            <tr>
                                <td><?= $incident['id'] ?></td>
                                <td><?= $incident['type'] ?></td>
                                <td><?= $incident['trip'] ?></td>
                                <td>
                                    <span class="badge <?= $incident['status'] === 'open' ? 'badge-danger' : 'badge-success' ?>">
                                        <?= $incident['status'] === 'open' ? 'Ouvert' : 'Résolu' ?>
                                    </span>
                                </td>
                                <td><?= $incident['time'] ?></td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            <?php endif; ?>
            
            <?php if ($page === 'users'): ?>
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Utilisateurs (<?= $stats['users_total'] ?>)</div>
                        <button class="btn btn-primary">+ Ajouter</button>
                    </div>
                    <p style="color: var(--text-secondary);">Liste des clients et chauffeurs...</p>
                </div>
            <?php endif; ?>
            
            <?php if ($page === 'analytics'): ?>
                <div class="stats-grid">
                    <div class="stat-card"><div class="label">Revenus sem.</div><div class="value">8.5M XAF</div></div>
                    <div class="stat-card"><div class="label">Trajets sem.</div><div class="value">2,450</div></div>
                    <div class="stat-card"><div class="label">Nouveaux users</div><div class="value">127</div></div>
                    <div class="stat-card"><div class="label">Note moyenne</div><div class="value">4.7 ⭐</div></div>
                </div>
                <div class="card"><div class="card-title">Graphiques Analytics</div><div class="chart">Visualisation des données</div></div>
            <?php endif; ?>
            
            <?php if ($page === 'settings'): ?>
                <div class="card">
                    <div class="card-title">Paramètres de l'Application</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;">
                        <div>
                            <h4 style="margin-bottom: 12px;">API Backend</h4>
                            <div class="form-group">
                                <label>URL de l'API</label>
                                <input type="text" value="<?= API_BASE ?>" readonly>
                            </div>
                        </div>
                        <div>
                            <h4 style="margin-bottom: 12px;">Zone Gabon</h4>
                            <div class="form-group">
                                <label>Fuseau horaire</label>
                                <input type="text" value="Africa/Libreville (GMT+1)" readonly>
                            </div>
                        </div>
                    </div>
                </div>
            <?php endif; ?>
            
        </main>
    </div>
<?php endif; ?>
</body>
</html>