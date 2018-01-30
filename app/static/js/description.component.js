'use strict';

class DescriptionComponent extends React.Component {

    constructor(props) {
        super(props);

        this.state = {table: this.props.name,
            description: this.props.description,
            category: this.props.category,
            edit: false,
            text: !this.props.description ? "" : this.props.description.description};

        this.handleChange = this.handleChange.bind(this);
        this.handleEdit = this.handleEdit.bind(this);
        this.handleSave = this.handleSave.bind(this);
        this.handleCancel = this.handleCancel.bind(this);
    }

    componentDidMount() {
        var $el = ReactDOM.findDOMNode(this);
        componentHandler.upgradeElements($el);
    }

    handleChange(e) {
        e.preventDefault();
        this.setState({text: e.target.value});
    }

    handleEdit(e) {
        e.preventDefault();
        this.setState({edit: true});
        setTimeout($.proxy(this.componentDidMount, this), 300);
    }

    handleSave(e) {
        e.preventDefault();

        var newObj = this.state.description || {};
        var self = this;

        newObj.description = this.state.text;
        newObj.user = loginSession.user();
        newObj.record_date = (new Date()).toISOString().replace("T", " ").split(".")[0];

        server.setMetadataTable(
            this.state.category,
            this.state.table,
            "description",
            newObj
        ).success(function(data){
            if(data.status !== true) {
                snackbar.show(data.response.message);
                return;
            }

            snackbar.show("Description added to " 
                + self.state.table 
                + ".");

        });

        this.setState({edit: false,
            description: newObj});
    }

    handleCancel(e) {
        e.preventDefault();
        this.setState(prevState => ({
            text: prevState.description,
            edit: !prevState.edit
        }));
    }

    render() {
        return (
            React.createElement(
                "div", 
                {className:"mdl-card wide auto-height mdl-shadow--2dp",
                    key: this.state.table},
                React.createElement(
                    "div",
                    {className: "mdl-card__title mdl-color--grey-200"},
                    React.createElement(
                        "h6",
                        {className: "mdl-card__title-text"},
                        this.state.table
                    )
                ),
                React.createElement(
                    "div",
                    {className: "mdl-card__supporting-text"},
                    (this.state.edit === true ?
                        React.createElement(
                            "div",
                            {className:"mdl-textfield wide mdl-js-textfield"},
                            React.createElement(
                                "textarea",
                                {className: "mdl-textfield__input",
                                    type: "text",
                                    rows: "5",
                                    id:"table-description",
                                    value: this.state.text,
                                    onChange: this.handleChange}),
                            React.createElement(
                                "label",
                                {className: "mdl-textfield__label",
                                    for: "table-description"},
                                "Please add a drescription for this table...")
                        ) : (
                            !this.state.description ? "Please add a description for this table..." :
                            (
                                React.createElement(
                                    "div",
                                    null,
                                    this.state.description.description,
                                    React.createElement("br", null),
                                    React.createElement("br", null),
                                    React.createElement("br", null),
                                    React.createElement("br", null),
                                    React.createElement("i", null, 
                                        "Last update by ",
                                        React.createElement(
                                            "strong",
                                            null,
                                            (this.state.description.user.firstName +
                                                " " + this.state.description.user.lastName)
                                        ),
                                        " - " + this.state.description.record_date
                                    )
                                )
                            )
                        )
                    )
                ),
                (this.state.edit === true ?
                    React.createElement(
                        "div",
                        {className: "mdl-card__actions mdl-card--border text-right"},
                        React.createElement(
                            "div",
                            {className: "inline"},
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
                        )
                    ) : null
                ),
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
                            "mode_edit"
                        ),
                    )
                )
            )
        );
    }
}
