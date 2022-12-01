import React, { Component } from "react";
import {
    Button,
    Modal,
    ModalHeader,
    ModalBody,
    ModalFooter,
    Form,
    FormGroup,
    Input,
    Label,
} from "reactstrap";
import TagsDropDown from "./TagsDropDown";


export default class TodoModal extends Component {
    constructor(props) {
        super(props);
        this.state = {
            activeItem: this.props.activeItem,
            confirmDelete: false
        };
    }

    handleChange = (e) => {
        let { name, value } = e.target;

        if (e.target.type === "checkbox") {
            value = e.target.checked;
        }

        const activeItem = { ...this.state.activeItem, [name]: value };

        this.setState({ activeItem });
    };

    handleUpdateTags = (tags) => {
        const activeItem = { ...this.state.activeItem, tags: tags }
        this.setState({ activeItem });
    };

    render() {
        const { toggle, onSaveItem, onDeleteItem } = this.props;
        return (
            <Modal isOpen={true} toggle={toggle}>
                <ModalHeader toggle={toggle}>Todo</ModalHeader>
                <ModalBody>
                    <Form>
                        <FormGroup>
                            <Label for="todo-title">Title</Label>
                            <Input
                                type="text"
                                id="todo-title"
                                name="title"
                                value={this.state.activeItem.title}
                                onChange={this.handleChange}
                                placeholder="Enter todo Title"
                            />
                        </FormGroup>
                        <FormGroup>
                            <Label for="todo-description">Description</Label>
                            <Input
                                type="textarea"
                                id="todo-description"
                                name="description"
                                value={this.state.activeItem.description}
                                onChange={this.handleChange}
                                placeholder="Enter todo description"
                            />
                        </FormGroup>
                        <FormGroup check>
                            <Label check>
                                <Input
                                    type="checkbox"
                                    name="completed"
                                    checked={this.state.activeItem.completed}
                                    onChange={this.handleChange}
                                />
                                Completed
                            </Label>
                        </FormGroup>
                        <FormGroup>
                            <hr />
                            <TagsDropDown
                                activeItem={this.state.activeItem}
                                onUpdateTags={this.handleUpdateTags}
                            />
                        </FormGroup>
                    </Form>
                </ModalBody>
                <ModalFooter
                    key='footer-buttons'
                    className="d-flex justify-content-between"
                >
                    <Button
                        color="danger"
                        onClick={() => onDeleteItem(this.state.activeItem)}
                    >
                        Delete
                    </Button>
                    <Button
                        color="primary"
                        onClick={() => onSaveItem(this.state.activeItem)}
                        disabled={
                            this.state.activeItem.title.length === 0
                            || this.state.activeItem.description.length === 0
                        }
                    >
                        Save
                    </Button>
                </ModalFooter>
            </Modal >
        );
    }
}
