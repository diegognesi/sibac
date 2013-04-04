CKEDITOR.plugins.add('ajaxsave',
    {
        init: function(editor)
        {
            var pluginName = 'ajaxsave';
            editor.addCommand( pluginName,
            {
                exec : function( editor )
                {
                    $.post(this.url, {
                        data : editor.getSnapshot()
                    } );
                },
                canUndo : true
            });
            editor.ui.addButton('Ajaxsave',
            {
                label: 'Save Ajax',
                command: pluginName,
                className : 'cke_button_save'
            });
        }
    });
