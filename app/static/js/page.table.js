var page = (function(page){

    "use strict";


    // COLUMNS
    var $colContainer = $(".columns-container");
    var $columns = $(".columns");
    var $columnsCount = $(".columns-count");

    //META
    var $tag = document.querySelector("#tag-component");
    var $related = document.querySelector("#related-component");
    var $other = document.querySelector("#other-component");


    // Table
    var $tableCompContainer = $(".tablecomp-container");
    var $tableComponent = $("#table-component"); 
    var TableElement, TagElement, OtherElement, RelatedElement;
    

    page.table = {

        init: function() {

        },

        render: function(table) {

            $columns.empty();

            // load columns
            server.getTableColumns(table)
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
                                             "href=\"/#column/"+ value +"&database="+ getDatabase() +"\">" +
                                             value +
                                         "</a>" +
                                     "</span>" +
                                 "</span>" +
                              "</li>"
                          );
                      });

                      $columns.html($row);
                      $columnsCount.html("&nbsp; ("+ data.response.data.length +")");
                      componentHandler.upgradeElements($columns[0]);

                  }).always(loader.start({container: $colContainer,
                                          element: $columns}));

            if(TableElement) {
                ReactDOM.unmountComponentAtNode($tableComponent[0]);
            }

            // get description
            server.getMetadataTable("table", table, "description")
                  .success(function(data){
                      if(data.status != true) {
                          snackbar.show(data.response.message);
                          return;
                      }

                      var obj = data.response.data[0];

                      TableElement = ReactDOM.render(
                          React.createElement(
                              DescriptionComponent,
                              {name: table, description: obj, category: "table"}),
                          $tableComponent[0]);

                  }).always(loader.start({container: $tableCompContainer, 
                      element:$tableComponent}));

            // related
            if(RelatedElement) {
                ReactDOM.unmountComponentAtNode($related);
            }

            RelatedElement = ReactDOM.render(
                React.createElement(
                    MetaElement,
                    {
                        name: "related",
                        category: "table",
                        table: table,
                        getDefer: server.getMetadataTable,
                        setDefer: server.setMetadataTable,
                        editable: false,
                        endpoint: "relation",
                        help: ("Related section, help's you to knwo to which" +
                            " table the current table could be related." +
                            " By clicking on any table you can see the relationship" +
                            " The related shown her are the ones approved by an user "+
                            " To see the user, please hover the table with your mouse.")
                    }
                ),
                $related);

            // tags
            if(TagElement) {
                ReactDOM.unmountComponentAtNode($tag);
            }
            
            TagElement = ReactDOM.render(
                React.createElement(
                    MetaElement,
                    {
                        name: "tag",
                        category: "table",
                        table: table,
                        getDefer: server.getMetadataTable,
                        setDefer: server.setMetadataTable,
                        help: ("Tag mean what it means everything that can be related" +
                            " to this table it could be a name, security type, ..." +
                            " e.i: INS_EXT_COD can be use to create a Bloomberg code, " +
                            " in this case I will add a tag \"Bloomberg\", \"BB\" or \"BBG\" "+
                            " to allow AI to be able to recognize a Thing during search. ")
                    }
                ),
                $tag);
            
            // others
            if(OtherElement) {
                ReactDOM.unmountComponentAtNode($other);
            }
                
            OtherElement = ReactDOM.render(
                    React.createElement(
                        MetaElement,
                        {
                            name: "other",
                            category: "table",
                            table: table,
                            getDefer: server.getMetadataTable,
                            setDefer: server.setMetadataTable,
                            help: ("Other section is also a tag, but contain abstract information. " +
                                   "e.i: Table ID_INST_QUOTE is use on screen 422 in Decalog, " +
                                   "you can add tag as \"422\", \"Security price entry\", \"Price\", ... " +
                                   "")
                        }
                    ),
                $other);

        }
    }

    return page;

})(page || {});
