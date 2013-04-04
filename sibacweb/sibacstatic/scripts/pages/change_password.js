$(function() {
  $("#changepwdform").validate({
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
      oldpassword: {required: true},
      newpassword: {required: true, password: true},
      newpasswordconfirm: {required: true, equalTo: "#newpassword"}
    },
    messages: {
      oldpassword: {required: "Inserire la vecchia password"},
      newpassword: {required: "Inserire la nuova password", password: "La password deve essere composta da almeno 8 caratteri e contenere almeno un numero e un segno di punteggiatura"},
      newpasswordconfirm: {required: "Reinserire la password", equalTo: "La password non coincide"}
    }
  });
});
