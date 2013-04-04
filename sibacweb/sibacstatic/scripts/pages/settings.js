// Gets the JSON representation of settings data.
function getSettingsData() {
  perm_array = [];
  var i = 0;
  $("#permissions-table tbody tr").each(function() {
    perm_array[i] = {
      dt_sid: $(this).find("td[name='dt-sid']").text(),
      is_active: $(this).find("input[name='is-active']").is(':checked'),
      access_level: $(this).find("select[name='dt-access-level']").val(),
      watermark_by_default: $(this).find("input[name='watermark-by-default']").is(':checked'),
      w_access_level: $(this).find("select[name='dt-w-access-level']").val(),
      visible_paragraphs: $(this).find("a[name='visible-paragraphs']").attr("data-paragraphs").split(","),
      default_expression: $(this).find("a[name='default-expression']").attr("data-expression")
    };
    i++;
  });
  data = {
    title: $("#site-title").val(),
    subtitle: $("#site-subtitle").val(),
    url: $("#site-url").val(),
    description: $("#site-description").val(),
    keywords: $("#site-keywords").val(),
    copyright: $("#site-copyright").val(),
    email: {
      email_from: $("#email-email-from").val(),
      username: $("#email-username").val(),
      password: $("#email-password").val(),
      host: $("#email-host").val(),
      port: $("#email-port").val(),
      use_tls: $('#email-use-tls').is(':checked'),
    },
    app_permissions: {
      registration_mode: $("input[name='registration_mode']:checked").val(),
      permissions: perm_array
    }
  };
  return JSON.stringify(data);
};

$(function() {
  $(".tabs").tabs();
  $("#save_settings").click(function(event) {
    event.preventDefault();
    var successMessage = "<p>Operazione conclusa con successo.</p><p>Eventuali cambiamenti all'intestazione o al piè di pagina del sito saranno visibili uscendo da questa pagina.</p>";
    sibacUi.ajaxCallWithDialogs("post", this.url, {json_data: getSettingsData()}, successMessage);
  });
  $("a[name='visible-paragraphs']").click(function(event) {
    event.preventDefault();
    var dt_sid = $(this).closest("tr").find("td[name='dt-sid']").text();
    sibacUi.selectParagraphs(dt_sid, $(this), "data-paragraphs");
  });
  $("a[name='default-expression']").click(function(event) {
    event.preventDefault();
    var dt_sid = $(this).closest("tr").find("td[name='dt-sid']").text();
    $t = $(this);
    sibacUi.setWhereConditions(dt_sid, $(this).attr("data-expression"), false, function(newExpression) {
      if (newExpression.length == 0) { newExpression = "None" };
      $t.attr("data-expression", newExpression);
      if (newExpression == "None") { $t.text("Non impostata"); }
      else if (newExpression.length > 20) { $t.text(newExpression.substr(0, 20) + "..."); }
      else { $t.text(newExpression); }
    });
  });
});
