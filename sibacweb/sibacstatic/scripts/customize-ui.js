/*
---------- This section adds custom methods to the query validator plugin.
*/

//Validation against regular expression.
$.validator.addMethod(
  "regex",
  function(value, element, regexp) {
      var re = new RegExp(regexp);
      return this.optional(element) || re.test(value);
    },
    "Il testo non soddisfa l'espressione regolare specificata."
);

//Validation of passwords.
$.validator.addMethod(
  "password",
  function(value, element, execute) {
      var re = new RegExp("^(?=.*\\d)(?=.*\\W)(?=.*[a-zA-Z]).{8,15}$");
      return this.optional(element) || !execute || re.test(value);
    },
    "La password deve avere tra gli 8 e i 15 caratteri, di cui almeno una lettera, un numero e un segno di punteggiatura."
);

/*
---------- This section contains jquery ui initialization functions.
*/

//This function enables jquery ui controls
$(function() {
  $(".accordion").accordion();
  $("input[type=submit], button").button();
  $("input[type=textbox].datepicker").datepicker();
});

/*
---------- This section is necessary to make ajax work with django csrf system.
*/

$.ajaxSetup({
     crossDomain: false,
     beforeSend: function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                     if (cookie.substring(0, name.length + 1) == (name + '=')) {
                         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                         break;
                     }
                 }
             }
             return cookieValue;
         }
         function csrfSafeMethod(method) {
             // these HTTP methods do not require CSRF protection
             return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
         }
         if (!csrfSafeMethod(settings.type)) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
     }
});



var sibacUi = {

  /*
  ---------- This section creates functions for messaging.
  */

  showDialog: function (title, message, modal, resizable) {
    var dlg_content = "<div id='tmp_msgDialog' class='hidden appdialog'";
    dlg_content += 'title="'
    if (title && title != "") {
      dlg_content += title
    }
    else {
      dlg_content += document.title;
    }
    dlg_content += '">';
    if (message) {
      dlg_content += message;
    };
    dlg_content += "</div>";
    // Append dialog.
    $(dlg_content).appendTo("body");
    // Show dialog
    $("#tmp_msgDialog").dialog({
      modal: modal,
      resizable: resizable,
      close: function(event, ui) { $("#tmp_msgDialog").remove(); },
      buttons: {
        'Ok': function() { $(this).dialog("close"); }
      }
    });
  },

  showWaitingDialog: function() {
    var dlg_content = "<div id='tmp_waitingDialog' class='hidden appdialog' title='SIBAC 1.0'><div class='spinner'><p>Operazione in corso. Attendere...</p></div></div>";
    $(dlg_content).appendTo("body");
    $("#tmp_waitingDialog").dialog({
      closeOnEscape: false,
      open: function(event, ui) { $(".waitingdialog .ui-dialog-titlebar").hide();},
      modal: true,
      resizable: false,
      minHeight: 0,
      dialogClass: "waitingdialog",
    });
  },

  closeWaitingDialog: function() {
    $("#tmp_waitingDialog").dialog("close");
    $("#tmp_waitingDialog").remove()
  },

  ajaxCallWithDialogs: function(method, postUrl, postData, successMessage, successFunction, errorFunction) {
    sibacUi.showWaitingDialog();
    $.ajax({
      type: method,
      url: postUrl,
      data: postData,
      timeout: 8000,
      success: function(data) {
        sibacUi.closeWaitingDialog();
        if (successMessage) {
          sibacUi.showDialog("", successMessage, true, false);
        }
        if (successFunction) {
          successFunction(data);
        }
      },
      error: function(jqXHR, textStatus, errorThrown) {
        sibacUi.closeWaitingDialog();
        sibacUi.showDialog("", "<p>Si è verificato un errore.</p><p>Tipo errore:" + textStatus + "</p><p>Errore: " + errorThrown + "</p>", true, false);
        if (errorFunction) {
          errorFunction(jqXHR, textStatus, errorThrown);
        }
      }
    });
  }
};
