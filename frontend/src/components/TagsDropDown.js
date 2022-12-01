import React, { Component, Fragment } from "react";
import {
    Badge,
    Dropdown,
    DropdownToggle,
    DropdownMenu,
    DropdownItem,
    Input,
    Button
} from "reactstrap";
import axios from "axios";

export default class TagsDropDown extends Component {
    constructor(props) {
        super(props);

        this.state = {
            activeItem: this.props.activeItem,
            newTag: { title: "" },
            allTags: [],
            toogle: false,
            tagIndex: 0
        };
    }

    toggle = () => {
        this.getTags()
        this.setState({
            toogle: !this.state.toogle
        });
    };

    getTags = () => {
        axios
            .get("/api/tags/")
            .then((res) => this.setState({ allTags: res.data }))
            .catch((err) => console.log(err));
    };

    updateTags = (tags) => {
        // remove same tags
        const filtered_tags = [...new Map(tags.map(item => [item['id'], item])).values()]
        const activeItem = { ...this.state.activeItem, tags: filtered_tags };
        this.setState({ activeItem });
        this.props.onUpdateTags(filtered_tags);
    };

    applyTag = (tag) => {
        axios
            .get("/api/tags/?title=" + tag.title)
            .then((res) => {
                if (res.data.length > 0) {
                    this.updateTags([...this.state.activeItem.tags, ...res.data])
                } else {
                    axios
                        .post("/api/tags/", tag)
                        .then((res) => this.updateTags([...this.state.activeItem.tags, res.data]))
                        .catch((err) => console.log(err));
                }
            })
            .catch((err) => console.log(err));
    };

    _clamp = (number, min, max) => {
        return Math.max(min, Math.min(number, max));
    };

    addTag = (e) => {
        let tag = { "title": e.target.value }
        let index = this.state.tagIndex
        if (e.key === "Enter") {
            this.applyTag({ ...tag });
            tag.title = ""
        }
        else if (e.type === "click") {
            this.applyTag({ ...tag });
            tag.title = ""
        }
        else if (e.key === "ArrowDown") {
            index = this._clamp(
                index + 1, 0, this.state.allTags.length
            )
            tag.title = this.state.allTags[index].title
        }
        else if (e.key === "ArrowUp") {
            index = this._clamp(
                index - 1, 0, this.state.allTags.length
            )
            tag.title = this.state.allTags[index].title
        }
        const newTag = { ...this.state.newTag, ...tag }

        this.setState({ newTag: newTag, tagIndex: index });
    };

    deleteTag = (e) => {
        const tags = this.state.activeItem.tags.filter(
            tag => (tag.id !== parseInt(e.target.value))
        )
        this.updateTags(tags);
    };

    renderTags = () => {
        return (
            <div className="container mt-2">
                <div className="row">
                    {this.state.activeItem.tags.map(tag => (
                        <Badge
                            className='mb-1 mr-1'
                            key={"tag-badge-" + tag.id.toString()}
                            color="secondary"
                            pill
                        >
                            {tag.title}
                            <Button
                                key={"tag-button-" + tag.id.toString()}
                                style={{ "boxShadow": "none" }}
                                name={tag.title}
                                value={tag.id}
                                outline
                                color="secondary"
                                size="sm"
                                onClick={this.deleteTag}
                            >
                                ╳
                            </Button>
                        </Badge>
                    ))}
                </div>
            </div>
        )
    };

    render() {
        return (
            <span>
                <Dropdown isOpen={this.state.toogle} toggle={this.toggle}>
                    <DropdownToggle tag="div" >
                        <Input
                            type="text"
                            id="tag-title"
                            name="tag"
                            value={this.state.newTag.title}
                            onChange={this.addTag}
                            onKeyDown={this.addTag}
                            autoComplete="off"
                            placeholder="Enter Tag Title"
                        />
                    </DropdownToggle>
                    <DropdownMenu>
                        {this.state.allTags.map(tag => (
                            <Fragment key={"tag-fragment-item" + tag.id.toString()}>
                                <DropdownItem
                                    key={"tag-dropdown-item-" + tag.id.toString()}
                                    value={tag.title}
                                    onClick={this.addTag}
                                    active={
                                        tag.title === this.state.allTags[this.state.tagIndex].title
                                    }
                                >
                                    {tag.title}
                                </DropdownItem>
                            </Fragment>
                        ))}
                    </DropdownMenu>
                </Dropdown>
                {this.renderTags()}
            </span>
        );
    }
}
