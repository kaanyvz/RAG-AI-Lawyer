document.addEventListener('DOMContentLoaded', function () {
    // Davalar sayfasındaki butonlara tıklama olaylarını ekle
    var buttons = document.querySelectorAll('.side-bar button');

    buttons.forEach(function(button) {
        button.addEventListener('click', function() {
            // Tüm butonlardan "active" sınıfını kaldır
            buttons.forEach(function(btn) {
                btn.classList.remove('active');
            });

            // Tıklanan butona "active" sınıfını ekle
            this.classList.add('active');

            // Butonun hangisine tıklandığına bağlı olarak goster fonksiyonunu çağır
            var targetId = this.getAttribute('id');
            var targetText = this.textContent;
            goster(targetId, targetText);
        });
    });
});





