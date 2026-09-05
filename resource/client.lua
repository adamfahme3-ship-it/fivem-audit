RegisterNetEvent('ac_audit:linkCode', function(code)
    TriggerEvent('chat:addMessage', { args = { '^2Audit', ('Your opt-in audit code is ^3%s^7. Run the published audit client and enter this code.'):format(code) } })
end)
