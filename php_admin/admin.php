<?php
/**
 * MobiTranz Desktop Admin - Application PHP
 * Interface d'administration complète style Windows 11 Fluent
 */

session_start();

define('API_BASE', getenv('API_BASE_URL') ?: 'http://localhost:8000');
define('APP_SECRET', getenv('APP_SECRET') ?: bin2hex(random_bytes(32)));

$page = $_GET['page'] ?? 'dashboard';
$user = $_SESSION['user'] ?? null;
$token = $_SESSION['token'] ?? null;
$apiError = null;

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
    if ($httpCode >= 200 && $httpCode < 300) {
        return json_decode($response, true);
    }
    return null;
}

function apiGetList($endpoint, $token) {
    $result = apiRequest($endpoint, 'GET', null, $token);
    if ($result === null) return null;
    if (isset($result['data'])) return $result['data'];
    if (isset($result['items'])) return $result['items'];
    if (isset($result['results'])) return $result['results'];
    return is_array($result) ? $result : null;
}

// Login handler
if ($page === 'login' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $phone = $_POST['phone'] ?? '';
    $password = $_POST['password'] ?? '';

    $result = apiRequest('/api/v1/auth/login', 'POST', [
        'phone' => $phone,
        'password' => $password
    ]);

    if ($result && isset($result['access_token'])) {
        session_regenerate_id(true);
        $_SESSION['token'] = $result['access_token'];
        $_SESSION['user'] = ['username' => $phone, 'role' => 'admin'];
        header('Location: ?page=dashboard');
        exit;
    }
    $apiError = 'Identifiants invalides';
}

if ($page === 'logout') {
    session_destroy();
    header('Location: ?page=login');
    exit;
}

// Fetch data based on current page
$stats = null;
$recent_trips = null;
$drivers = null;
$vehicles = null;
$payments = null;
$incidents = null;
$users = null;

if ($user && $token) {
    switch ($page) {
        case 'dashboard':
            $stats = apiRequest('/api/v1/admin/dashboard/kpis', 'GET', null, $token);
            $recent_trips = apiGetList('/api/v1/trips?limit=5', $token);
            break;
        case 'trips':
            $recent_trips = apiGetList('/api/v1/trips', $token);
            break;
        case 'drivers':
            $drivers = apiGetList('/api/v1/drivers', $token);
            break;
        case 'vehicles':
            $vehicles = apiGetList('/api/v1/vehicles', $token);
            break;
        case 'payments':
            $payments = apiGetList('/api/v1/payments', $token);
            break;
        case 'incidents':
            $incidents = apiGetList('/api/v1/incidents', $token);
            break;
        case 'users':
            $users = apiGetList('/api/v1/users', $token);
            break;
    }
}
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

        /* Error */
        .unavailable { color: var(--danger); text-align: center; padding: 24px; font-size: 16px; }
    </style>
</head>
<body>
<?php if (!$user && $page !== 'login'): ?>
    <div class="login-page">
        <div class="login-box">
            <h1>🚕 MobiTranz</h1>
            <p>Administration</p>
            <?php if ($apiError): ?>
                <div class="badge badge-danger" style="margin-bottom: 16px; display: block;"><?= $apiError ?></div>
            <?php endif; ?>
            <form method="POST">
                <div class="form-group">
                    <label>Téléphone</label>
                    <input type="text" name="phone" required placeholder="+241 XX XX XX XX">
                </div>
                <div class="form-group">
                    <label>Mot de passe</label>
                    <input type="password" name="password" required placeholder="••••••••">
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%;">Se connecter</button>
            </form>
            <p style="margin-top: 16px; font-size: 12px;">Authentification requise</p>
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
                        <span><?= htmlspecialchars($user['username'] ?? 'admin') ?></span>
                    </div>
                </div>
            </header>
            
            <?php if ($page === 'dashboard'): ?>
                <?php if ($stats === null): ?>
                    <div class="unavailable">Service indisponible</div>
                <?php else: ?>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="label">Trajets aujourd'hui</div>
                        <div class="value"><?= $stats['trips_today'] ?? 'N/A' ?></div>
                        <div class="trend">↑ 12% vs hier</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Revenus aujourd'hui</div>
                        <div class="value"><?= isset($stats['revenue_today']) ? number_format($stats['revenue_today'], 0, ',', ' ') : 'N/A' ?> XAF</div>
                        <div class="trend">↑ 8% vs hier</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Chauffeurs en ligne</div>
                        <div class="value"><?= $stats['active_drivers'] ?? 'N/A' ?></div>
                        <div class="trend"><?= ($stats['active_vehicles'] ?? 'N/A') ?> véhicules</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Incidents ouverts</div>
                        <div class="value"><?= $stats['incidents'] ?? 'N/A' ?></div>
                        <div class="trend">↓ 3 vs semaine dernière</div>
                    </div>
                </div>
                <?php endif; ?>
                
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Trajets Récents</div>
                        <a href="?page=trips" class="btn btn-secondary">Voir tout</a>
                    </div>
                    <?php if ($recent_trips === null): ?>
                        <div class="unavailable">Service indisponible</div>
                    <?php elseif (empty($recent_trips)): ?>
                        <p style="color: var(--text-secondary); text-align: center; padding: 24px;">Aucun trajet récent</p>
                    <?php else: ?>
                    <table>
                        <thead>
                            <tr><th>ID</th><th>Client</th><th>Trajet</th><th>Montant</th><th>Statut</th></tr>
                        </thead>
                        <tbody>
                            <?php foreach ($recent_trips as $trip): ?>
                            <tr>
                                <td><?= htmlspecialchars($trip['id'] ?? '') ?></td>
                                <td><?= htmlspecialchars($trip['client'] ?? $trip['rider_name'] ?? $trip['user_name'] ?? '') ?></td>
                                <td><?= htmlspecialchars($trip['route'] ?? $trip['pickup_location'] ?? '') ?> → <?= htmlspecialchars($trip['destination'] ?? '') ?></td>
                                <td><?= isset($trip['amount']) ? number_format($trip['amount'], 0, ',', ' ') : 'N/A' ?> XAF</td>
                                <td>
                                    <?php $s = $trip['status'] ?? ''; ?>
                                    <?php if ($s === 'completed' || $s === 'terminé'): ?>
                                        <span class="badge badge-success">Terminé</span>
                                    <?php elseif ($s === 'pending' || $s === 'en_cours' || $s === 'in_progress'): ?>
                                        <span class="badge badge-warning">En cours</span>
                                    <?php elseif ($s === 'cancelled' || $s === 'annulé'): ?>
                                        <span class="badge badge-danger">Annulé</span>
                                    <?php else: ?>
                                        <span class="badge badge-info"><?= htmlspecialchars($s) ?></span>
                                    <?php endif; ?>
                                </td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                    <?php endif; ?>
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
                    <?php if ($recent_trips === null): ?>
                        <div class="unavailable">Service indisponible</div>
                    <?php elseif (empty($recent_trips)): ?>
                        <p style="color: var(--text-secondary); text-align: center; padding: 24px;">Aucun trajet</p>
                    <?php else: ?>
                    <table>
                        <thead>
                            <tr><th>ID</th><th>Client</th><th>Trajet</th><th>Montant</th><th>Statut</th><th>Actions</th></tr>
                        </thead>
                        <tbody>
                            <?php foreach ($recent_trips as $trip): ?>
                            <tr>
                                <td><?= htmlspecialchars($trip['id'] ?? '') ?></td>
                                <td><?= htmlspecialchars($trip['client'] ?? $trip['rider_name'] ?? $trip['user_name'] ?? '') ?></td>
                                <td><?= htmlspecialchars($trip['route'] ?? $trip['pickup_location'] ?? '') ?> → <?= htmlspecialchars($trip['destination'] ?? '') ?></td>
                                <td><?= isset($trip['amount']) ? number_format($trip['amount'], 0, ',', ' ') : 'N/A' ?> XAF</td>
                                <td>
                                    <?php $s = $trip['status'] ?? ''; ?>
                                    <?php if ($s === 'completed' || $s === 'terminé'): ?>
                                        <span class="badge badge-success">Terminé</span>
                                    <?php elseif ($s === 'pending' || $s === 'en_cours' || $s === 'in_progress'): ?>
                                        <span class="badge badge-warning">En cours</span>
                                    <?php elseif ($s === 'cancelled' || $s === 'annulé'): ?>
                                        <span class="badge badge-danger">Annulé</span>
                                    <?php else: ?>
                                        <span class="badge badge-info"><?= htmlspecialchars($s) ?></span>
                                    <?php endif; ?>
                                </td>
                                <td><a href="#" class="btn btn-secondary" style="padding: 4px 12px; font-size: 12px;">Détails</a></td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                    <?php endif; ?>
                </div>
            <?php endif; ?>
            
            <?php if ($page === 'drivers'): ?>
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Chauffeurs</div>
                        <button class="btn btn-primary">+ Ajouter chauffeur</button>
                    </div>
                    <?php if ($drivers === null): ?>
                        <div class="unavailable">Service indisponible</div>
                    <?php elseif (empty($drivers)): ?>
                        <p style="color: var(--text-secondary); text-align: center; padding: 24px;">Aucun chauffeur</p>
                    <?php else: ?>
                    <table>
                        <thead>
                            <tr><th>ID</th><th>Nom</th><th>Téléphone</th><th>Véhicule</th><th>Statut</th><th>Note</th></tr>
                        </thead>
                        <tbody>
                            <?php foreach ($drivers as $driver): ?>
                            <tr>
                                <td><?= htmlspecialchars($driver['id'] ?? '') ?></td>
                                <td><?= htmlspecialchars($driver['name'] ?? $driver['full_name'] ?? $driver['first_name'] ?? '') ?></td>
                                <td><?= htmlspecialchars($driver['phone'] ?? $driver['phone_number'] ?? '') ?></td>
                                <td><?= htmlspecialchars($driver['vehicle'] ?? $driver['vehicle_plate'] ?? $driver['vehicle_id'] ?? '') ?></td>
                                <td>
                                    <?php $s = $driver['status'] ?? ''; ?>
                                    <?php if ($s === 'online' || $s === 'en_ligne' || $s === 'active'): ?>
                                        <span class="badge badge-success">En ligne</span>
                                    <?php else: ?>
                                        <span class="badge badge-warning">Hors ligne</span>
                                    <?php endif; ?>
                                </td>
                                <td><?= $driver['rating'] ?? 'N/A' ?> ⭐</td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                    <?php endif; ?>
                </div>
            <?php endif; ?>
            
            <?php if ($page === 'vehicles'): ?>
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Véhicules</div>
                        <button class="btn btn-primary">+ Ajouter véhicule</button>
                    </div>
                    <?php if ($vehicles === null): ?>
                        <div class="unavailable">Service indisponible</div>
                    <?php elseif (empty($vehicles)): ?>
                        <p style="color: var(--text-secondary); text-align: center; padding: 24px;">Aucun véhicule</p>
                    <?php else: ?>
                    <table>
                        <thead>
                            <tr><th>ID</th><th>Plaque</th><th>Marque</th><th>Modèle</th><th>Chauffeur</th><th>Statut</th></tr>
                        </thead>
                        <tbody>
                            <?php foreach ($vehicles as $v): ?>
                            <tr>
                                <td><?= htmlspecialchars($v['id'] ?? '') ?></td>
                                <td><?= htmlspecialchars($v['plate'] ?? $v['plate_number'] ?? $v['license_plate'] ?? '') ?></td>
                                <td><?= htmlspecialchars($v['brand'] ?? $v['make'] ?? '') ?></td>
                                <td><?= htmlspecialchars($v['model'] ?? '') ?></td>
                                <td><?= htmlspecialchars($v['driver'] ?? $v['driver_name'] ?? '') ?></td>
                                <td>
                                    <?php $s = $v['status'] ?? ''; ?>
                                    <?php if ($s === 'active' || $s === 'available'): ?>
                                        <span class="badge badge-success">Actif</span>
                                    <?php elseif ($s === 'maintenance'): ?>
                                        <span class="badge badge-warning">Maintenance</span>
                                    <?php else: ?>
                                        <span class="badge badge-info"><?= htmlspecialchars($s) ?></span>
                                    <?php endif; ?>
                                </td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                    <?php endif; ?>
                </div>
            <?php endif; ?>
            
            <?php if ($page === 'payments'): ?>
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Historique des Paiements</div>
                    </div>
                    <?php if ($payments === null): ?>
                        <div class="unavailable">Service indisponible</div>
                    <?php elseif (empty($payments)): ?>
                        <p style="color: var(--text-secondary); text-align: center; padding: 24px;">Aucun paiement</p>
                    <?php else: ?>
                    <table>
                        <thead>
                            <tr><th>ID</th><th>Méthode</th><th>Montant</th><th>Statut</th><th>Date</th></tr>
                        </thead>
                        <tbody>
                            <?php foreach ($payments as $payment): ?>
                            <tr>
                                <td><?= htmlspecialchars($payment['id'] ?? '') ?></td>
                                <td><?= htmlspecialchars($payment['method'] ?? $payment['payment_method'] ?? $payment['type'] ?? '') ?></td>
                                <td><?= isset($payment['amount']) ? number_format($payment['amount'], 0, ',', ' ') : 'N/A' ?> XAF</td>
                                <td>
                                    <?php $s = $payment['status'] ?? ''; ?>
                                    <?php if ($s === 'success' || $s === 'completed' || $s === 'confirmé'): ?>
                                        <span class="badge badge-success">Succès</span>
                                    <?php elseif ($s === 'pending' || $s === 'en_attente'): ?>
                                        <span class="badge badge-warning">En attente</span>
                                    <?php else: ?>
                                        <span class="badge badge-danger">Échec</span>
                                    <?php endif; ?>
                                </td>
                                <td><?= htmlspecialchars($payment['time'] ?? $payment['created_at'] ?? $payment['date'] ?? '') ?></td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                    <?php endif; ?>
                </div>
            <?php endif; ?>
            
            <?php if ($page === 'incidents'): ?>
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Incidents</div>
                        <button class="btn btn-primary" style="background: var(--danger);">+ Signaler</button>
                    </div>
                    <?php if ($incidents === null): ?>
                        <div class="unavailable">Service indisponible</div>
                    <?php elseif (empty($incidents)): ?>
                        <p style="color: var(--text-secondary); text-align: center; padding: 24px;">Aucun incident</p>
                    <?php else: ?>
                    <table>
                        <thead>
                            <tr><th>ID</th><th>Type</th><th>Trajet</th><th>Statut</th><th>Date</th></tr>
                        </thead>
                        <tbody>
                            <?php foreach ($incidents as $incident): ?>
                            <tr>
                                <td><?= htmlspecialchars($incident['id'] ?? '') ?></td>
                                <td><?= htmlspecialchars($incident['type'] ?? $incident['incident_type'] ?? $incident['title'] ?? '') ?></td>
                                <td><?= htmlspecialchars($incident['trip'] ?? $incident['trip_id'] ?? '') ?></td>
                                <td>
                                    <?php $s = $incident['status'] ?? ''; ?>
                                    <?php if ($s === 'open' || $s === 'ouvert'): ?>
                                        <span class="badge badge-danger">Ouvert</span>
                                    <?php elseif ($s === 'resolved' || $s === 'résolu' || $s === 'closed'): ?>
                                        <span class="badge badge-success">Résolu</span>
                                    <?php else: ?>
                                        <span class="badge badge-info"><?= htmlspecialchars($s) ?></span>
                                    <?php endif; ?>
                                </td>
                                <td><?= htmlspecialchars($incident['time'] ?? $incident['created_at'] ?? $incident['date'] ?? '') ?></td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                    <?php endif; ?>
                </div>
            <?php endif; ?>
            
            <?php if ($page === 'users'): ?>
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Utilisateurs <?= $users !== null ? '(' . count($users) . ')' : '' ?></div>
                        <button class="btn btn-primary">+ Ajouter</button>
                    </div>
                    <?php if ($users === null): ?>
                        <div class="unavailable">Service indisponible</div>
                    <?php elseif (empty($users)): ?>
                        <p style="color: var(--text-secondary); text-align: center; padding: 24px;">Aucun utilisateur</p>
                    <?php else: ?>
                    <table>
                        <thead>
                            <tr><th>ID</th><th>Nom</th><th>Téléphone</th><th>Rôle</th><th>Statut</th><th>Inscrit</th></tr>
                        </thead>
                        <tbody>
                            <?php foreach ($users as $u): ?>
                            <tr>
                                <td><?= htmlspecialchars($u['id'] ?? '') ?></td>
                                <td><?= htmlspecialchars($u['name'] ?? $u['full_name'] ?? $u['first_name'] ?? '') ?></td>
                                <td><?= htmlspecialchars($u['phone'] ?? $u['phone_number'] ?? '') ?></td>
                                <td><?= htmlspecialchars($u['role'] ?? $u['user_type'] ?? 'client') ?></td>
                                <td>
                                    <?php $s = $u['status'] ?? ''; ?>
                                    <?php if ($s === 'active' || $s === 'actif'): ?>
                                        <span class="badge badge-success">Actif</span>
                                    <?php elseif ($s === 'pending' || $s === 'en_attente'): ?>
                                        <span class="badge badge-warning">En attente</span>
                                    <?php elseif ($s === 'blocked' || $s === 'banni'): ?>
                                        <span class="badge badge-danger">Banni</span>
                                    <?php else: ?>
                                        <span class="badge badge-info"><?= htmlspecialchars($s) ?></span>
                                    <?php endif; ?>
                                </td>
                                <td><?= htmlspecialchars($u['created_at'] ?? $u['date'] ?? $u['created'] ?? '') ?></td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                    <?php endif; ?>
                </div>
            <?php endif; ?>
            
            <?php if ($page === 'analytics'): ?>
                <?php
                $analytics = apiRequest('/api/v1/analytics/summary', 'GET', null, $token);
                ?>
                <div class="stats-grid">
                    <div class="stat-card"><div class="label">Revenus sem.</div><div class="value"><?= isset($analytics['weekly_revenue']) ? number_format($analytics['weekly_revenue'], 0, ',', ' ') : 'N/A' ?> XAF</div></div>
                    <div class="stat-card"><div class="label">Trajets sem.</div><div class="value"><?= number_format($analytics['weekly_trips'] ?? 0, 0, ',', ' ') ?></div></div>
                    <div class="stat-card"><div class="label">Nouveaux users</div><div class="value"><?= $analytics['new_users'] ?? 'N/A' ?></div></div>
                    <div class="stat-card"><div class="label">Note moyenne</div><div class="value"><?= $analytics['avg_rating'] ?? 'N/A' ?> ⭐</div></div>
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
