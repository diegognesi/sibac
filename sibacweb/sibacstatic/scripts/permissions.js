// Displays the paragraph list dialog.
sibacUi.selectParagraphs = function(dt_sid, item_with_data, attribute_name) {
  var dlg_content = "<div id='paragraph-selector' class='hidden appdialog'><h2>Paragrafi visualizzati scheda <span id='p-selector-dt_sid'></span></h2><p>Seleziona i paragrafi che gli utenti con permessi di accesso alle schede di questo tipo potranno visualizzare di default.<br/>Questa impostazione potrà essere sovrascritta dalle impostazioni specifiche di ogni singolo utente registrato.</p><div id='p-selector-chk-container'></div></div>";
  $(dlg_content).appendTo("body");
  $("#paragraph-selector #p-selector-dt_sid").text(dt_sid);
  $chkContainer = $("#paragraph-selector #p-selector-chk-container");
  $chkContainer.empty().html("<p>Recupero dei dati in corso...</p>").addClass("spinner");
  var para_names = null;
  $("#paragraph-selector").dialog({
    title: document.title,
    modal: true,
    resizable: true,
    minWidth: 450,
    buttons: [
      {
        id: "p-selector-btn-cancel",
        text: "Annulla",
        click: function() { $(this).dialog("close"); $(this).remove(); }
      },
      {
        id: "p-selector-btn-ok",
        text: "Ok",
        click: function() {
          var selected_items_sid = [];
          var all_checked = true;
          $("#p-selector-chk-container input[type='checkbox']").each(function(index) {
            if ($(this).is(':checked')) {
              selected_items_sid.push($(this).attr("data-p-sid"));
            }
            else {
              all_checked = false;
            }
          });
          if (all_checked) {
            item_with_data.attr(attribute_name, "*");
          }
          else {
            item_with_data.attr(attribute_name, selected_items_sid.join(","));
          }
          $(this).dialog("close");
          $(this).remove();
        }
      }
    ]
  });
  $chkContainer.css( { 'max-height' : '150px' } );
  $.ajax({
    type: "GET",
    url: "/ajaxrequest/get_dt_paragraphs?dt_sid=" + dt_sid,
    timeout: 8000,
    success: function(data) {
      $chkContainer.empty().removeClass("spinner");
      paragraphs = data.paragraphs;
      var selected_items = item_with_data.attr(attribute_name).split(",");
      for(i=0; i< paragraphs.length; i++) {
        var p_sid = paragraphs[i].sid;
        var p_text = paragraphs[i].sid + " - " + paragraphs[i].alt;
        var chk_id = "p-selector-chk-" + p_sid;
        var inputHtml = "<input type='checkbox' id='" + chk_id + "' data-p-sid='" + p_sid + "'";
        if (selected_items.length > 0 && (selected_items[0] == "*" || $.inArray(p_sid, selected_items) != -1))
        {
          inputHtml += " checked='checked'";
        }
        inputHtml += " /><label for='" + chk_id + "' >" + p_text + "</label><br/>"
        $(inputHtml).appendTo("#paragraph-selector #p-selector-chk-container");
      }
    },
    error: function(jqXHR, textStatus, errorThrown) {
      $("#p-selector-btn-ok").button("disable");
      $chkContainer.removeClass("spinner").html("<p>Si è verificato un errore. Chiudere questa finestra e riprovare.</p><p>Tipo errore:" + textStatus + "</p><p>Errore: " + errorThrown + "</p>");
    }
  });
};

// Display a dialog window that will ask for a search condition.
sibacUi.setWhereConditions = function(dt_sid, expression, allow_for_storage_only, successFunction) {
  var dlg_content = "<div id='where-selector' class='hidden appdialog' style='height:20%'><div><h2>Condizioni di ricerca</h2><p>Imposta le condizioni di ricerca che verranno attribuite di default ai nuovi utenti.</p></div><textarea id='where-condition-text' rows='5' cols='60' style='resize: none; width: 100%; height: 60%; margin:0px; padding:0px;'></textarea></div>";
  $(dlg_content).appendTo("body");
  if (expression && expression != "None") {
    $("#where-condition-text").val(expression);
  }
  else {
    $("#where-condition-text").val("SELECT * FROM [" + dt_sid + "] WHERE ");
  }
  $('#where-selector').dialog({
    title: document.title,
    modal: true,
    resizable: true,
    buttons: {
      'Annulla': function() { $(this).dialog("close"); $(this).remove(); },
      'Ok': function() {
        newExpression = $("#where-condition-text").val();
        if (!newExpression || $.trim(newExpression) == "" || $.trim(newExpression) == "SELECT * FROM [" + dt_sid + "] WHERE") {
            successFunction("");
            $("#where-selector").dialog("close").remove();
        }
        else {
          sibacUi.ajaxCallWithDialogs("get", "/ajaxrequest/validate_search_expression?expr=" + escape(newExpression) + "&for_storage_only=true", "", "",
            function(data) {
              if (!data.is_valid) {
                escapedErrors = [];
                for (i=0; i< data.errors.length; i++)
                {
                  escapedErrors[i] = $('<div/>').text(data.errors[i]).html()
                }
                expErrors = escapedErrors.join("<br/>");
                sibacUi.showDialog("", "<h2>Correggere i seguenti errori:</h2><p>" + expErrors + "</p>", true, false);
              }
              else {
                if (successFunction) {
                  successFunction(data.expr);
                }
                $("#where-selector").dialog("close").remove();
              }
            }
          );
        } 
      }
    }
  });
};
