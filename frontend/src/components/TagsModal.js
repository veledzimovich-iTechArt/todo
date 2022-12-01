import React, { Component } from "react";
import {
    Modal,
    ModalHeader,
    ModalBody,
} from "reactstrap";

export default class TagsModal extends Component {
    constructor(props) {
        super(props);
        this.state = {
            allTags: this.props.allTags,
        };
    }

    deleteTag = (item) => {
        this.props.onDeleteTag(item)

        const allTags = this.state.allTags.filter((tag) => tag.id !== item.id)
        this.setState({ allTags })
    };

    renderTags = () => {
        return this.state.allTags.map((item) => (
            <li
                key={item.id}
                className="list-group-item d-flex justify-content-between align-items-center"
            >
                <span className="tag-title mr-2">
                    {item.title}
                </span>
                <span>
                    <button
                        className="btn btn-danger"
                        onClick={() => this.deleteTag(item)}
                    >
                        Delete
                    </button>
                </span>
            </li>
        ));
    };

    render() {
        return (
            <Modal isOpen={true} toggle={this.props.toggle}>
                <ModalHeader toggle={this.props.toggle}>Tags</ModalHeader>
                <ModalBody>
                    {this.renderTags()}
                </ModalBody>
            </Modal >
        );
    }
}
