function savePageContent( editor ) {
  successMessage = "<p>I contenuti della pagina sono stati salvati.</p>";
  sibacUi.ajaxCallWithDialogs("post", this.url, {page_content: editor.getData()}, successMessage);
}

/*
Add the 'Save' button.
*/
CKEDITOR.plugins.registered['save'] =
{
  init : function( editor )
  {
    var command = editor.addCommand( 'save', {
    modes : { wysiwyg:1, source:1 },
    exec : function( editor ) {
      savePageContent( editor );
    }
  });
  editor.ui.addButton( 'Save',{label : '',command : 'save'});
  }
}
