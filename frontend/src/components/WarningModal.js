import React, { Component } from "react";
import {
    Modal,
    ModalHeader,
    ModalBody,
    Form,
    FormGroup,
    Label,
} from "reactstrap";


export default class WarningModal extends Component {
    constructor(props) {
        super(props);
        this.state = {
            errors: this.props.getErrors()
        }
    };

    render() {
        const { toggle } = this.props;
        const errors = { ...this.state.errors };
        const all_errors = [];
        for (var key in errors)
            all_errors.push(errors[key]);

        return (
            <Modal isOpen={true} toggle={toggle} >
                <ModalHeader toggle={toggle}>Warning</ModalHeader>
                <ModalBody>
                    <Form>
                        <FormGroup>
                            <Label for="warning-title">{all_errors}</Label>
                        </FormGroup>
                    </Form>
                </ModalBody>
            </Modal >
        );
    }
}
