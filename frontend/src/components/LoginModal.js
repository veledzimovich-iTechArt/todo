import React, { Component } from "react";
import {
    Button,
    Modal,
    ModalHeader,
    ModalBody,
    ModalFooter,
    Form,
    FormGroup,
    FormFeedback,
    Input,
    Label
} from "reactstrap";
import { modalTypes } from "../types/modalTypes";

export default class LoginModal extends Component {
    constructor(props) {
        super(props);
        this.state = {
            errors: this.props.getErrors(),
            username: '',
            email: '',
            password: ''
        };
    }

    handleChange = (e) => {
        let { name, value } = e.target;
        this.setState({ ...this.state, [name]: value, errors: {} });
    };

    render() {
        const { type, toggle, onOK } = this.props;
        let is_sign_up = true;
        let title = 'Sign Up';
        if (type === modalTypes.SignIn) {
            is_sign_up = false;
            title = 'Sign In';
        }
        const handleOK = () => {
            const { username, password, email } = this.state
            onOK(type, username, password, email)
        }
        const handleDisabled = () => {
            return (
                this.state.username.length === 0
                || this.state.password.length === 0
                || (is_sign_up && this.state.email.length === 0)
            )
        }
        const errors = { ...this.state.errors };
        const handleUsernameErrors = () => {
            return errors.non_field_errors ? (
                <FormFeedback>{errors.non_field_errors}</FormFeedback>
            ) : errors.username ? (
                <FormFeedback>{errors.username}</FormFeedback>
            ) : null
        }
        const handleEmailErrors = () => {
            return errors.email ? (
                <FormFeedback>{errors.email}</FormFeedback>
            ) : null
        }
        const handlePasswordErrors = () => {
            return errors.non_field_errors ? (
                <FormFeedback>{errors.non_field_errors}</FormFeedback>
            ) : errors.password ? (
                <FormFeedback>{errors.password}</FormFeedback>
            ) : null
        }

        return (
            <Modal isOpen={true} toggle={toggle}>
                <ModalHeader toggle={toggle}>{title}</ModalHeader>
                <ModalBody>
                    <Form>
                        <FormGroup>
                            <Label for="login-title">Username</Label>
                            <Input
                                type="text"
                                id="login-username"
                                name="username"
                                value={this.state.username}
                                onChange={this.handleChange}
                                placeholder="Enter Username"
                                invalid={
                                    (errors.non_field_errors && errors.non_field_errors.length > 0)
                                    || (errors.username && errors.username.length > 0)
                                }
                            />
                            {handleUsernameErrors()}
                        </FormGroup>
                        {
                            is_sign_up ? (
                                <FormGroup>
                                    <Label for="login-email">Email</Label>
                                    <Input
                                        type="text"
                                        id="login-email"
                                        name="email"
                                        value={this.state.email}
                                        onChange={this.handleChange}
                                        placeholder="Enter Email"
                                        invalid={errors.email && errors.email.length > 0}
                                    />
                                    {handleEmailErrors()}
                                </FormGroup>
                            ) : null
                        }
                        <FormGroup>
                            <Label for="login-password">Password</Label>
                            <Input
                                type="password"
                                id="login-password"
                                name="password"
                                value={this.state.password}
                                onChange={this.handleChange}
                                placeholder="Enter Password"
                                invalid={
                                    (errors.non_field_errors && errors.non_field_errors.length > 0)
                                    || (errors.password && errors.password.length > 0)
                                }
                            />
                            {handlePasswordErrors()}
                        </FormGroup>
                    </Form>
                </ModalBody>
                <ModalFooter
                    key='footer-buttons'
                >
                    <Button
                        color="primary"
                        onClick={handleOK}
                        disabled={handleDisabled()}
                    >
                        OK
                    </Button>
                </ModalFooter>
            </Modal >
        );
    }
}
