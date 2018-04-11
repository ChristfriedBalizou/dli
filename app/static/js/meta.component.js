"use strict";

class MetaElement extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            name: this.props.name,
            table: this.props.table,
            editable: this.props.editable === false ? false : (this.props.editable || true),
            get: this.props.getDefer,
            set: this.props.setDefer,
            category: this.props.category,
            edit: false,
            data: [],
            text: '',
            endpoint: this.props.endpoint || "search",
            loading: true,
            error: false,
            errorMsg: null,
            help: this.props.help 
        };
        
        this.handleChange = this.handleChange.bind(this);
        this.handleEdit = this.handleEdit.bind(this);
        this.handleSave = this.handleSave.bind(this);
        this.handleCancel = this.handleCancel.bind(this);
        this.handleDelete = this.handleDelete.bind(this);
        this.initElement = this.initElement.bind(this);

        this.editTemplate = this.editTemplate.bind(this);
        this.displayTemplate = this.displayTemplate.bind(this);

    }

    initElement() {
        var self = this;
        var $el  = ReactDOM.findDOMNode(self);
        
        this.setState({
            loading: true,
            error: false,
            errorMsg: null
        });

        // get server data
        this.state
            .get(this.state.category, this.state.table, this.state.name)
            .success(function(data){
                if(data.status !== true){
                    snackbar.show(data.response.message);
                    self.setState({error: true, errorMsg: data.response.message});
                    return;
                }
                self.setState({data: data.response.data || []});
            }).always(function(){
                self.setState({loading: false});
                componentHandler.upgradeElements($el);
            });
    }

    componentDidMount() {
        var self = this;
        var $el  = ReactDOM.findDOMNode(self);

        componentHandler.upgradeElements($el);

        if(this.state.edit === true){
            // do not run the init method
            // on edit mode
            return;
        }
        // init component
        this.initElement();
    }

    handleChange(e) {
        e.preventDefault();
        this.setState({text: e.target.value});
    }


    handleDelete(e) {
        e.preventDefault();

        var list = this.state.data;
        var self = this;
        var $el  = ReactDOM.findDOMNode(this);

        var strRegex = new RegExp(e.target.dataset.value, 'i');
        var i = list.findIndex(function(o){
            return strRegex.test(o.description);
        });
       
        if(i === -1){
            return;
        }

        var obj = {
            "description": e.target.dataset.value,
            "delete": true,
        };
        
        this.state
            .set(this.state.category,
                 this.state.table,
                 this.state.name,
                 obj)
            .success(function(data){

                if(data.status !== true) {
                    snackbar.show(data.response.message);
                    return;
                }

                snackbar.show(obj.description 
                              + " removed from " 
                              + self.state.name 
                              + ".");
            })
            .always(function(){
                componentHandler.upgradeElements($el);
            });

        list.splice(i, 1);
        this.setState({data: list});
    }

    handleEdit(e) {
        e.preventDefault();
        this.setState({edit: true});
        setTimeout($.proxy(this.componentDidMount, this), 300);
    }

    handleSave(e) {
        e.preventDefault();
        var self = this;
        var $el  = ReactDOM.findDOMNode(this);
        var list = this.state.data;
        

        var newObj = {
            "description": this.state.text,
            "type": this.state.name,
        };
        
        var strRegex = new RegExp(newObj.description, 'i');
        
        var i = this.state.data.findIndex(function(o){
            return strRegex.test(o.description);
        });

        if(i !== -1) {
            this.setState({text: '', edit: false});
            return;
        }

        this.state
            .set(this.state.category,
                 this.state.table,
                 this.state.name,
                 newObj)
            .success(function(data){

                if(data.status !== true) {
                    snackbar.show(data.response.message);
                    return;
                }

                snackbar.show(newObj.description 
                              + " added to " 
                              + self.state.name 
                              + ".");
            })
            .always(function(){
                componentHandler.upgradeElements($el);
            });
        
        $.extend(newObj, {
            "user": loginSession.user(),
            "record_date": (new Date()).toISOString().replace("T", " ").split(".")[0]
        });

        this.setState(prevState => ({
            edit: false,
            data: prevState.data.concat(newObj),
            text: ''
        }));
    }
    
    handleCancel(e) {
        this.setState({
            text: '',
            edit: false
        });
    }


    displayTemplate() {
        return (this.state.loading === true ?
            React.createElement(
                "div",
                {className: "loader"}
            ) :
            (this.state.error === false ?
                (this.state.data.length === 0 ?
                    "" :
                    this.state.data.map(obj =>
                        (React.createElement(
                            "span",
                            {className: "mdl-chip marg-left-5px " + (this.state.editable ? "mdl-chip--deletable": ""),
                                key: obj.description + "-chip",
                                id: obj.description + "-chip"},
                            React.createElement(
                                "a",
                                {className: "mdl-chip__text no-decoration mdl-color-text--blue",
                                    href:("/#" + [this.state.endpoint,
                                        obj.description,
                                        this.state.table].join("/") + "&database=" + getDatabase())},
                                obj.description
                            ),
                            (this.state.editable ? 
                                React.createElement(
                                    "button",
                                    {className: "mdl-chip__action",
                                        type: "button"},
                                    React.createElement(
                                        "i",
                                        {className: "material-icons",
                                         "data-value": obj.description,
                                         onClick: this.handleDelete},
                                        "cancel"
                                    )
                                ): null),
                            React.createElement(
                                "div",
                                {className: "mdl-tooltip mdl-tooltip--top text-left",
                                 for: obj.description + "-chip"},
                                React.createElement(
                                    "strong",
                                    null,
                                    "Created by " + obj.user.firstName + " " + obj.user.lastName
                                ),
                                React.createElement("br", null),
                                "on " + obj.record_date
                            )
                        )
                        ))
                ) : this.state.errorMsg
            )
        );
    }

    editTemplate() {
        return (
            React.createElement(
                "div", 
                {className: "mdl-textfield fill mdl-js-textfield mdl-textfield--floating-label"}, 
                React.createElement(
                    "input",
                    {className: "mdl-textfield__input",
                     type: "text",
                     autofocus: "",
                     id: this.state.name + "-id",
                     onChange: this.handleChange,
                     value: this.state.text}
                ),
                React.createElement(
                    "label",
                    {className: "mdl-textfield__label",
                     for: this.state.name + "-id"},
                    "Type a " + this.state.name + " here..."
                )
            )
        );
    }

    render() {
        return (
            React.createElement(
                "div",
                {className: "mdl-card auto-height wide mdl-shadow--2dp",
                 key: this.state.table + this.state.name},
                React.createElement(
                    "div",
                    {className: "mdl-card__title"},
                    React.createElement(
                        "h6",
                        {className: "mdl-card__title-text mdl-color-text--grey-400 font-size1"},
                        capitalize(this.state.name)
                    )
                ),
                React.createElement(
                    "div",
                    {className: "help"},
                    this.state.help
                ),
                React.createElement(
                    "div",
                    {className: "mdl-card__supporting-text fill-96-5"},
                    (this.state.edit === true ? this.editTemplate(): this.displayTemplate())
                ),
                (this.state.editable == true ? 
                    React.createElement(
                        "div",
                        {className: "mdl-card__menu"},
                        React.createElement(
                            "button",
                            {className: "mdl-button mdl-button--icon mdl-js-button",
                                onClick: this.handleEdit},
                            React.createElement(
                                "i",
                                {className: "material-icons"},
                                "add"
                            ),
                        )
                    ): null
                ),
                (this.state.edit === true ?
                    React.createElement(
                        "div",
                        {className: "inline text-right mdl-card__actions mdl-card--border"},
                        React.createElement(
                            "button",
                            {className: "mdl-button mdl-js-button mdl-color-text--indigo",
                                onClick: this.handleSave},
                            "Save"),
                        React.createElement(
                            "button",
                            {className: "mdl-button mdl-js-button",
                                onClick: this.handleCancel},
                            "Cancel")
                    ) : null)
            )
        );

        function capitalize(str) {
            return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
        }
    }
}
