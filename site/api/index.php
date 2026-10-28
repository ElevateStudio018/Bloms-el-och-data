<?php
/*
 * Bloms El & Data – API för adminpanelen och kontaktformuläret.
 *
 * Kräver PHP 7.4+ (cURL för AI-funktionen). Data sparas i ../data/ som skyddas av .htaccess.
 * Inställningar i config.php (se config.sample.php).
 *
 * Publika anrop:   POST ?action=lead
 * Inloggade anrop: me, login, logout, publish, history, history_get, users, user_add, user_delete,
 *                  password, leads, lead_update, lead_delete, ai, config
 */
declare(strict_types=1);

const ROOT = __DIR__ . '/..';
const DATA = ROOT . '/data';
const ITER = 210000;

$cfg = is_file(__DIR__ . '/config.php') ? (array) require __DIR__ . '/config.php' : [];
$cfg += [
    'anthropic_api_key' => '',
    'notify_email' => 'info@blomsel.se',
    'mail_from' => 'no-reply@blomsel.se',
    'model' => 'claude-opus-5-5',
];

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store');

if (!is_dir(DATA)) {
    @mkdir(DATA, 0750, true);
}
if (!is_file(DATA . '/.htaccess')) {
    @file_put_contents(DATA . '/.htaccess', "Require all denied\nDeny from all\n");
}

$https = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') || (($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '') === 'https');
session_name('blomsadmin');
session_set_cookie_params(['lifetime' => 0, 'path' => '/', 'secure' => $https, 'httponly' => true, 'samesite' => 'Strict']);
session_start();

$action = (string) ($_GET['action'] ?? '');
$method = $_SERVER['REQUEST_METHOD'] ?? 'GET';

// ------------------------------------------------------------------ hjälpfunktioner
function out($data, int $code = 200): void
{
    http_response_code($code);
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

function body(): array
{
    $raw = file_get_contents('php://input') ?: '';
    if (strlen($raw) > 12 * 1024 * 1024) {
        out(['error' => 'För stor förfrågan'], 413);
    }
    $j = json_decode($raw, true);
    return is_array($j) ? $j : [];
}

function readj(string $file, $default)
{
    if (!is_file($file)) {
        return $default;
    }
    $j = json_decode((string) file_get_contents($file), true);
    return $j === null ? $default : $j;
}

function writej(string $file, $data): void
{
    $tmp = $file . '.' . bin2hex(random_bytes(4)) . '.tmp';
    file_put_contents($tmp, json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT), LOCK_EX);
    rename($tmp, $file);
}

function need(?string $role = null): void
{
    if (empty($_SESSION['user'])) {
        out(['error' => 'Inte inloggad'], 401);
    }
    if ($role === 'admin' && ($_SESSION['role'] ?? '') !== 'admin') {
        out(['error' => 'Kräver administratör'], 403);
    }
}

function post_only(): void
{
    global $method;
    if ($method !== 'POST') {
        out(['error' => 'Fel metod'], 405);
    }
    // Skydd mot förfalskade anrop från andra sajter: kräver en egen header (sätts av adminpanelen)
    if (($_SERVER['HTTP_X_BLOMS'] ?? '') !== '1') {
        out(['error' => 'Ogiltig förfrågan'], 400);
    }
}

function client_key(): string
{
    return hash('sha256', ($_SERVER['REMOTE_ADDR'] ?? '') . '|bloms');
}

/** Enkel spärr per IP. $limit försök per $window sekunder. */
function rate(string $bucket, int $limit, int $window): bool
{
    $file = DATA . '/rate.json';
    $all = readj($file, []);
    $now = time();
    $key = $bucket . ':' . client_key();
    $hits = array_values(array_filter($all[$key] ?? [], fn($t) => $t > $now - $window));
    if (count($hits) >= $limit) {
        return false;
    }
    $hits[] = $now;
    $all[$key] = $hits;
    foreach ($all as $k => $v) {
        if (!array_filter($v, fn($t) => $t > $now - 86400)) {
            unset($all[$k]);
        }
    }
    writej($file, $all);
    return true;
}

function users(): array
{
    $file = DATA . '/users.json';
    if (!is_file($file) && is_file(ROOT . '/admin/users.json')) {
        // Första körningen: flytta in konton från den statiska adminpanelen
        @copy(ROOT . '/admin/users.json', $file);
    }
    $u = readj($file, ['version' => 1, 'users' => []]);
    return $u['users'] ?? [];
}

function save_users(array $list): void
{
    writej(DATA . '/users.json', ['version' => 1, 'users' => array_values($list)]);
}

function verifier(string $pass, string $saltHex, int $iter): string
{
    $bits = hash_pbkdf2('sha256', $pass, (string) hex2bin($saltHex), $iter, 64, true);
    return bin2hex(substr($bits, 0, 32));
}

function make_user(string $name, string $pass, string $role, ?string $created = null): array
{
    $salt = bin2hex(random_bytes(16));
    return ['username' => $name, 'role' => $role, 'salt' => $salt, 'iterations' => ITER,
        'verifier' => verifier($pass, $salt, ITER), 'token' => null, 'created' => $created ?: gmdate('c')];
}

function public_user(array $u): array
{
    return ['username' => $u['username'], 'role' => $u['role'], 'created' => $u['created'] ?? null];
}

function valid_name(string $n): bool
{
    return (bool) preg_match('/^[\w.\-@]{3,40}$/u', $n);
}

function clean(string $s, int $max): string
{
    $s = trim(preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F]/u', '', $s) ?? '');
    return mb_substr($s, 0, $max);
}

// ------------------------------------------------------------------ publika anrop
if ($action === 'lead') {
    if ($method !== 'POST') {
        out(['error' => 'Fel metod'], 405);
    }
    $b = body();
    if (!empty($b['website'])) {
        out(['ok' => true]); // honungsfälla för robotar
    }
    if (!rate('lead', 5, 3600)) {
        out(['error' => 'För många förfrågningar. Ring oss gärna istället.'], 429);
    }
    $lead = [
        'id' => bin2hex(random_bytes(6)),
        'created' => gmdate('c'),
        'status' => 'ny',
        'name' => clean((string) ($b['namn'] ?? ''), 120),
        'phone' => clean((string) ($b['telefon'] ?? ''), 40),
        'email' => clean((string) ($b['epost'] ?? ''), 160),
        'type' => clean((string) ($b['arende'] ?? ''), 80),
        'message' => clean((string) ($b['meddelande'] ?? ''), 5000),
        'page' => clean((string) ($b['sida'] ?? ''), 120),
        'notes' => [],
    ];
    if ($lead['name'] === '' || $lead['message'] === '' || ($lead['email'] === '' && $lead['phone'] === '')) {
        out(['error' => 'Fyll i namn, meddelande och e-post eller telefon.'], 422);
    }
    if ($lead['email'] !== '' && !filter_var($lead['email'], FILTER_VALIDATE_EMAIL)) {
        out(['error' => 'E-postadressen ser inte rätt ut.'], 422);
    }
    $file = DATA . '/leads.json';
    $fp = fopen($file . '.lock', 'c');
    flock($fp, LOCK_EX);
    $all = readj($file, []);
    array_unshift($all, $lead);
    writej($file, $all);
    flock($fp, LOCK_UN);

    // Avisering via e-post (fungerar om webbhotellet tillåter mail())
    $to = $cfg['notify_email'];
    if ($to && function_exists('mail')) {
        $subject = '=?UTF-8?B?' . base64_encode('Ny förfrågan: ' . ($lead['type'] ?: 'blomsel.se')) . '?=';
        $text = "Ny förfrågan via blomsel.se\n\nNamn: {$lead['name']}\nTelefon: {$lead['phone']}\nE-post: {$lead['email']}\nÄrende: {$lead['type']}\n\n{$lead['message']}\n\nSe alla förfrågningar i adminpanelen.";
        $headers = "From: {$cfg['mail_from']}\r\nContent-Type: text/plain; charset=UTF-8\r\n";
        if ($lead['email'] !== '') {
            $headers .= 'Reply-To: ' . $lead['email'] . "\r\n";
        }
        @mail($to, $subject, $text, $headers);
    }
    out(['ok' => true]);
}

// ------------------------------------------------------------------ inloggning
if ($action === 'me') {
    if (empty($_SESSION['user'])) {
        out(['error' => 'Inte inloggad', 'server' => true], 401);
    }
    out(['user' => $_SESSION['user'], 'role' => $_SESSION['role'], 'server' => true]);
}

if ($action === 'login') {
    post_only();
    if (!rate('login', 8, 900)) {
        out(['error' => 'För många försök. Vänta en stund och försök igen.'], 429);
    }
    $b = body();
    $name = mb_strtolower(trim((string) ($b['username'] ?? '')));
    $pass = (string) ($b['password'] ?? '');
    foreach (users() as $u) {
        if (mb_strtolower($u['username']) === $name && hash_equals($u['verifier'], verifier($pass, $u['salt'], (int) ($u['iterations'] ?? ITER)))) {
            session_regenerate_id(true);
            $_SESSION['user'] = $u['username'];
            $_SESSION['role'] = $u['role'];
            out(['user' => $u['username'], 'role' => $u['role']]);
        }
    }
    usleep(400000);
    out(['error' => 'Fel användarnamn eller lösenord.'], 401);
}

if ($action === 'logout') {
    post_only();
    $_SESSION = [];
    session_destroy();
    out(['ok' => true]);
}

// ------------------------------------------------------------------ allt nedan kräver inloggning
need();

if ($action === 'config') {
    out(['ai' => $cfg['anthropic_api_key'] !== '', 'model' => $cfg['model'], 'notify' => $cfg['notify_email']]);
}

if ($action === 'publish') {
    post_only();
    $b = body();
    $c = $b['content'] ?? null;
    if (!is_array($c) || !isset($c['text']) || !is_array($c['text'])) {
        out(['error' => 'Innehållet har fel format.'], 422);
    }
    // Uppladdade bilder sparas som filer
    $uploads = is_array($c['uploads'] ?? null) ? $c['uploads'] : [];
    foreach ($uploads as $path => $dataUrl) {
        if (!preg_match('#^img/uploads/[a-z0-9\-]{1,80}\.jpg$#', (string) $path) || !preg_match('#^data:image/jpeg;base64,#', (string) $dataUrl)) {
            continue;
        }
        $bin = base64_decode(substr((string) $dataUrl, 23), true);
        if ($bin === false || strlen($bin) > 6 * 1024 * 1024 || !@getimagesizefromstring($bin)) {
            continue;
        }
        @mkdir(ROOT . '/img/uploads', 0755, true);
        file_put_contents(ROOT . '/' . $path, $bin, LOCK_EX);
    }
    $c['uploads'] = new stdClass();
    $c['updated'] = gmdate('c');
    foreach (['text', 'link', 'img', 'meta', 'hero', 'settings'] as $k) {
        if (!isset($c[$k]) || $c[$k] === []) {
            $c[$k] = new stdClass(); // tomma objekt ska förbli {} i JSON
        }
    }
    $file = ROOT . '/content.json';
    @mkdir(DATA . '/history', 0750, true);
    if (is_file($file)) {
        writej(DATA . '/history/' . gmdate('Ymd-His') . '-' . bin2hex(random_bytes(2)) . '.json',
            ['at' => gmdate('c'), 'by' => $_SESSION['user'], 'message' => clean((string) ($b['message'] ?? ''), 200), 'content' => readj($file, [])]);
        $old = glob(DATA . '/history/*.json') ?: [];
        sort($old);
        foreach (array_slice($old, 0, max(0, count($old) - 60)) as $f) {
            @unlink($f);
        }
    }
    writej($file, $c);
    out(['ok' => true, 'content' => $c]);
}

if ($action === 'history') {
    $list = [];
    $files = glob(DATA . '/history/*.json') ?: [];
    rsort($files);
    foreach (array_slice($files, 0, 40) as $f) {
        $j = readj($f, []);
        $list[] = ['id' => basename($f, '.json'), 'at' => $j['at'] ?? null, 'by' => $j['by'] ?? null, 'message' => $j['message'] ?? ''];
    }
    out(['history' => $list]);
}

if ($action === 'history_get') {
    $id = (string) ($_GET['id'] ?? '');
    if (!preg_match('/^[0-9a-f\-]{10,40}$/', $id) || !is_file(DATA . "/history/$id.json")) {
        out(['error' => 'Versionen finns inte'], 404);
    }
    out(['content' => readj(DATA . "/history/$id.json", [])['content'] ?? []]);
}

if ($action === 'users') {
    out(['users' => array_map('public_user', users())]);
}

if ($action === 'user_add') {
    post_only();
    need('admin');
    $b = body();
    $name = trim((string) ($b['username'] ?? ''));
    $pass = (string) ($b['password'] ?? '');
    $role = ($b['role'] ?? '') === 'admin' ? 'admin' : 'redaktor';
    if (!valid_name($name) || mb_strlen($pass) < 12) {
        out(['error' => 'Användarnamn 3–40 tecken och lösenord minst 12 tecken.'], 422);
    }
    $list = users();
    foreach ($list as $u) {
        if (mb_strtolower($u['username']) === mb_strtolower($name)) {
            out(['error' => 'Användarnamnet finns redan.'], 409);
        }
    }
    $list[] = make_user($name, $pass, $role);
    save_users($list);
    out(['users' => array_map('public_user', $list)]);
}

if ($action === 'user_delete') {
    post_only();
    need('admin');
    $name = (string) (body()['username'] ?? '');
    if ($name === $_SESSION['user']) {
        out(['error' => 'Du kan inte ta bort dig själv.'], 422);
    }
    $list = array_values(array_filter(users(), fn($u) => $u['username'] !== $name));
    if (!array_filter($list, fn($u) => $u['role'] === 'admin')) {
        out(['error' => 'Minst en administratör måste finnas.'], 422);
    }
    save_users($list);
    out(['users' => array_map('public_user', $list)]);
}

if ($action === 'password') {
    post_only();
    $b = body();
    $old = (string) ($b['old'] ?? '');
    $new = (string) ($b['new'] ?? '');
    if (mb_strlen($new) < 12) {
        out(['error' => 'Nytt lösenord måste vara minst 12 tecken.'], 422);
    }
    $list = users();
    foreach ($list as $i => $u) {
        if ($u['username'] === $_SESSION['user']) {
            if (!hash_equals($u['verifier'], verifier($old, $u['salt'], (int) ($u['iterations'] ?? ITER)))) {
                out(['error' => 'Nuvarande lösenord stämmer inte.'], 403);
            }
            $list[$i] = make_user($u['username'], $new, $u['role'], $u['created'] ?? null);
            save_users($list);
            out(['ok' => true]);
        }
    }
    out(['error' => 'Användaren finns inte'], 404);
}

if ($action === 'leads') {
    out(['leads' => readj(DATA . '/leads.json', [])]);
}

if ($action === 'lead_update' || $action === 'lead_delete') {
    post_only();
    $b = body();
    $id = (string) ($b['id'] ?? '');
    $file = DATA . '/leads.json';
    $fp = fopen($file . '.lock', 'c');
    flock($fp, LOCK_EX);
    $all = readj($file, []);
    $found = false;
    foreach ($all as $i => $l) {
        if (($l['id'] ?? '') !== $id) {
            continue;
        }
        $found = true;
        if ($action === 'lead_delete') {
            array_splice($all, $i, 1);
            break;
        }
        $allowed = ['ny', 'kontaktad', 'offert', 'vunnen', 'forlorad'];
        if (isset($b['status']) && in_array($b['status'], $allowed, true)) {
            $all[$i]['status'] = $b['status'];
        }
        if (!empty($b['note'])) {
            $all[$i]['notes'][] = ['at' => gmdate('c'), 'by' => $_SESSION['user'], 'text' => clean((string) $b['note'], 2000)];
        }
        if (isset($b['value'])) {
            $all[$i]['value'] = max(0, (int) $b['value']);
        }
        break;
    }
    writej($file, $all);
    flock($fp, LOCK_UN);
    if (!$found) {
        out(['error' => 'Förfrågan finns inte'], 404);
    }
    out(['leads' => $all]);
}

if ($action === 'ai') {
    post_only();
    if ($cfg['anthropic_api_key'] === '') {
        out(['error' => 'AI är inte aktiverat. Lägg in en API-nyckel i api/config.php.'], 503);
    }
    if (!rate('ai', 60, 3600)) {
        out(['error' => 'För många AI-anrop just nu. Vänta en stund.'], 429);
    }
    if (!function_exists('curl_init')) {
        out(['error' => 'Webbhotellet saknar cURL, som AI-funktionen behöver.'], 500);
    }
    $b = body();
    $req = [
        'model' => $cfg['model'],
        'max_tokens' => min(16000, max(256, (int) ($b['max_tokens'] ?? 8000))),
        'system' => (string) ($b['system'] ?? ''),
        'messages' => is_array($b['messages'] ?? null) ? $b['messages'] : [],
        'output_config' => ['effort' => 'medium'],
        'fallbacks' => 'default',
    ];
    if (!empty($b['tools']) && is_array($b['tools'])) {
        $req['tools'] = $b['tools'];
    }
    $stream = !empty($b['stream']);
    if ($stream) {
        $req['stream'] = true;
    }
    $ch = curl_init('https://api.anthropic.com/v1/messages');
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_HTTPHEADER => [
            'content-type: application/json',
            'x-api-key: ' . $cfg['anthropic_api_key'],
            'anthropic-version: 2026-10-21',
            'anthropic-beta: server-side-fallback-2026-07-01',
        ],
        CURLOPT_POSTFIELDS => json_encode($req, JSON_UNESCAPED_UNICODE),
        CURLOPT_TIMEOUT => 300,
    ]);
    if ($stream) {
        header('Content-Type: text/event-stream; charset=utf-8');
        header('X-Accel-Buffering: no');
        while (ob_get_level()) {
            ob_end_flush();
        }
        curl_setopt($ch, CURLOPT_WRITEFUNCTION, function ($c, $chunk) {
            echo $chunk;
            flush();
            return strlen($chunk);
        });
        curl_exec($ch);
        curl_close($ch);
        exit;
    }
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    $res = curl_exec($ch);
    $code = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    http_response_code($code ?: 502);
    echo $res ?: json_encode(['error' => 'Inget svar från AI-tjänsten']);
    exit;
}

out(['error' => 'Okänd åtgärd'], 404);
