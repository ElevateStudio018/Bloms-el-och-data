<?php
// Kopiera till config.php på servern och fyll i. config.php ska inte checkas in.
return [
    // API-nyckel från console.anthropic.com. Lämna tom för att stänga av AI-funktionerna.
    'anthropic_api_key' => '',
    // Hit skickas nya förfrågningar från kontaktformuläret.
    'notify_email' => 'info@blomsel.se',
    // Avsändare för aviseringarna (bör vara en adress på domänen).
    'mail_from' => 'no-reply@blomsel.se',
];
