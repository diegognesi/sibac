$(function() {
  $("#loginform").validate({
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
      username: {required: true},
      password: {required: true}
    },
    messages: {
      username: {required: "Inserire il nome utente"},
      password: {required: "Inserire la password"}
    }
  });
});
