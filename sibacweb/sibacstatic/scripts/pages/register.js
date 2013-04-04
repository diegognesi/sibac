$(function() {
  $("#registerform").validate({
    errorPlacement: function(error, element) {
      if(!error.is(':empty')) {
      $(element).qtip("destroy").qtip({
        content: { text: error.text() },
        show: { event: false, ready: true},
        hide: false,
        position: { at: 'right-center', my: 'left-center' },
        style: {classes: 'qtip-shadow qtip-red'}
      });
      }
      else { $(element).qtip("destroy"); }
    },
    success: function(element) { $(element).removeData(".qtip"); },
    rules: {
      name: {required: true},
      surname: {required: true},
      email: {required: true, email: true},
      username: {required: true, minlength: 3, maxlength: 15},
      password: {required: true, password: true},
      passwordrepeat: {required: true, equalTo: "#password"}
    },
    messages: {
      name: {required: "Inserire il nome di battesimo"},
      surname: {required: "Inserire il cognome"},
      email: {required: "Inserire l'e-mail", email: "Il testo inserito non è un indirizzo e-mail valido"},
      username: {
          required: "Inserire il nome utente",
          minlength: "Richiesti almeno 3 caratteri",
          maxlength: "Richiesti al massimo 15 caratteri"
      },
      password: {required: "Inserire la password", password: "La password deve essere composta da almeno 8 caratteri e contenere almeno un numero e un segno di punteggiatura"},
      passwordrepeat: {required: "Reinserire la password", equalTo: "La password non coincide"}
    }
  });
});
