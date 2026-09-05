local function createSession(source)
    local identifiers = GetPlayerIdentifiers(source)
    local payload = json.encode({ player = GetPlayerName(source), identifiers = identifiers })
    PerformHttpRequest(Config.apiBaseUrl .. '/sessions', function(status, body)
        if status ~= 201 then print(('[ac_audit] Could not create audit session: HTTP %s'):format(status)); return end
        local response = json.decode(body)
        TriggerClientEvent('ac_audit:linkCode', source, response.code)
    end, 'POST', payload, { ['Content-Type']='application/json', ['X-Server-Secret']=Config.serverSecret })
end

RegisterCommand('auditcode', function(source)
    if source == 0 then print('[ac_audit] This command is for an in-game player.'); return end
    createSession(source)
end, false)
