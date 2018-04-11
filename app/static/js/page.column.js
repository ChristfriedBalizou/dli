var page = (function(page){
    'use strict';

    //META
    var $tag = document.querySelector("#tagcol-component");
    var $other = document.querySelector("#othercol-component");

    // TABLES
    var $tableContainer = $(".tables-container");
    var $tables = $(".tables");
    var $tableCount = $(".tables-count");
    
    // Table
    var $columnsCompContainer = $(".column-container");
    var $columnComponent = $("#column-component"); 
    var DescriptionElement, TagColElement, OtherColElement;

    page.column = {
        init: function() {
        },

        render: function(column) {
            
            if(DescriptionElement) {
                ReactDOM.unmountComponentAtNode($columnComponent[0]);
            }

            // get description
            server.getMetadataTable("column", column, "description")
                  .success(function(data){
                      if(data.status != true) {
                          snackbar.show(data.response.message);
                          return;
                      }

                      var obj = data.response.data[0];

                      DescriptionElement = ReactDOM.render(
                          React.createElement(
                              DescriptionComponent,
                              {name: column, description: obj, category: "column"}),
                          $columnComponent[0]);

                  }).always(loader.start({container: $columnsCompContainer, 
                      element:$columnComponent}));


            server.getTablesByColumn(column)
                  .success(function(data){
                      if(data.status != true) {
                          snackbar.show(data.response.message);
                          return;
                      }
                      
                      var $row = data.response.data.map(function(value){
                          return (
                              "<li class=\"mdl-list__item\">" +
                                 "<span class=\"mdl-list__item-primary-content\">" +
                                     "<span class=\"mdl-chip\">" +
                                         "<a class=\"mdl-chip__text no-decoration\"" +
                                             "href=\"/#table/"+ value +"&database="+ getDatabase() +"\">" +
                                             value +
                                         "</a>" +
                                     "</span>" +
                                 "</span>" +
                              "</li>"
                          );
                      });

                      $tableCount.html("&nbsp; (" + data.response.data.length + ")");
                      $tables.html($row);
                      componentHandler.upgradeElements($tables[0]);
                  }).always(loader.start({container: $tableContainer, element: $tables}));

            // tags
            if(TagColElement) {
                ReactDOM.unmountComponentAtNode($tag);
            }
            
            TagColElement = ReactDOM.render(
                React.createElement(
                    MetaElement,
                    {
                        name: "tag",
                        category: "column",
                        table: column,
                        getDefer: server.getMetadataTable,
                        setDefer: server.setMetadataTable,
                        help: ("Everything that can relate the current column with" +
                            " another column should be listed here" +
                            " e.i: If INST_NUM is CONT_NUM in another table, if current column is" +
                            " INST_NUM, in this case I will add a tag \"CONT_NUM\""+
                            " to allow AI to be able to recognize relations during search. ")
                    }
                ),
                $tag);
            
            // others
            if(OtherColElement) {
                ReactDOM.unmountComponentAtNode($other);
            }
                
            OtherColElement = ReactDOM.render(
                    React.createElement(
                        MetaElement,
                        {
                            name: "other",
                            category: "column",
                            table: column,
                            getDefer: server.getMetadataTable,
                            setDefer: server.setMetadataTable,
                            help: ("Other section is also a tag, but contain abstract information. " +
                                   "e.i: If this column is used for Bloomberg code or a certain security key, " +
                                   "you can add tag as \"Bloomberg\", \"ISIN\", \"Rick\", ... " +
                                   "")
                        }
                    ),
                $other);
        }
    };

    return page;

})(page || {});
