function automaticallyCloseAlerts() {
    window.setTimeout(function() {
        document.querySelectorAll('.alert').forEach(function(alert) {
            var alertInstance = bootstrap.Alert.getOrCreateInstance(alert);
            alertInstance.close();
        });
    }, 3000);
}