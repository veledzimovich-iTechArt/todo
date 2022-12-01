import React, { Component } from "react";
import { Badge, Button, ButtonGroup, Card } from 'reactstrap';
import LoginModal from "./components/LoginModal";
import TodoModal from "./components/TodoModal";
import TagsModal from "./components/TagsModal";
import WarningModal from "./components/WarningModal";
import { modalTypes } from "./types/modalTypes";
import { getCookies, setCookie, removeCookie } from "./utils/cookieUtil";
import axios from "axios";

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      viewCompleted: false,
      todoList: [],
      allTags: [],
      tagsSelected: [],
      openedModalType: null,
      activeItem: {
        title: "",
        description: "",
        completed: false,
        tags: []
      },
      errors: {}
    };
  }

  // backend request
  componentDidMount() {
    this.refreshPage();
  }

  getTodos = () => {
    let tags = this.state.tagsSelected.join('&tags=')
    let url = tags ? "/api/todos/?tags=" + tags : "/api/todos/"
    axios
      .get(url)
      .then((res) => this.setState({ todoList: res.data }))
      .catch((err) => console.log(err));
  };

  getTags = () => {
    axios
      .get("/api/tags/")
      .then((res) => this.setState({ allTags: res.data }))
      .catch((err) => console.log(err));
  };

  refreshPage = () => {
    const cookies = getCookies(document)
    // add X-CSRFToken in reqest headers
    axios.defaults.headers.common['X-CSRFToken'] = cookies['csrftoken'];
    // check that cookies expired
    if (!cookies['loggedUserName']) {
      axios.get('/api/logout/').catch((err) => console.log(err));
    }

    this.getTags();
    this.getTodos();
  };

  // todo modal
  handleSubmitItem = (item) => {
    this.closeModal();

    if (item.id) {
      axios
        .put(`/api/todos/${item.id}/`, item)
        .then((res) => this.refreshPage())
        .catch((err) => this.handleErrors(err, modalTypes.Warning));
      return;
    }
    axios
      .post("/api/todos/", item)
      .then((res) => this.refreshPage())
      .catch((err) => this.handleErrors(err, modalTypes.Warning));
  };

  // todos
  createItem = () => {
    const item = {
      title: "", description: "", completed: false, tags: []
    };

    this.setState({ activeItem: item, openedModalType: modalTypes.Todo });
  };

  editItem = (item) => {
    this.setState({ activeItem: item, openedModalType: modalTypes.Todo });
  };

  handleDeleteItem = (item) => {
    this.closeModal();
    axios
      .delete(`/api/todos/${item.id}/`)
      .then((res) => this.refreshPage())
      .catch((err) => this.handleErrors(err, modalTypes.Warning));
  };

  // tag modal
  handleDeleteTag = (item) => {
    this.selectTag(item.id);
    const tagsSelected = this.state.tagsSelected.filter((id) => id !== item.id)
    this.setState({ tagsSelected });

    axios
      .delete(`/api/tags/${item.id}/`)
      .then((res) => this.refreshPage())
      .catch((err) => this.handleErrors(err, modalTypes.Warning));
  };

  // tags
  selectTag = (selected) => {
    const index = this.state.tagsSelected.indexOf(selected);
    if (index < 0) {
      this.state.tagsSelected.push(selected);
    } else {
      this.state.tagsSelected.splice(index, 1);
    }

    this.setState({ tagsSelected: [...this.state.tagsSelected] });

    // filter by tags
    this.getTodos();
  };

  // tabs
  displayCompleted = (status) => {
    if (status) {
      return this.setState({ viewCompleted: true });
    }
    return this.setState({ viewCompleted: false });
  };

  // login
  getErrors = () => {
    const errors = this.state.errors;
    this.setState({ errors: {} });
    return errors
  }

  handleLogin = (type, username, password, email) => {
    if (type === modalTypes.SignIn) {
      this.signIn(username, password);
    } else {
      this.signUp(username, password, email);
    }
  };

  handleErrors = (err, type) => {
    if (err.response) {
      if (
        err.response.status === 400
        || err.response.status === 403
      ) {
        this.setState({ errors: { ...err.response.data } });
        this.openModal(type);
      } else if (err.response.status === 500) {
        console.log(err);
      } else {
        Object.keys(err.response.data).forEach(key => {
          alert(...err.response.data[key])
        });
      }
    } else {
      console.log(err);
    }
  };

  signIn = (username, password) => {
    this.closeModal();
    axios
      .post('/api/login/', { "username": username, "password": password })
      .then((res) => {
        setCookie(document, "loggedUserName", res.data.username);
        this.refreshPage();
      })
      .catch((err) => this.handleErrors(err, modalTypes.SignIn));
  };

  signUp = (username, password, email) => {
    this.closeModal();
    axios
      .post('/api/register/', {
        "username": username, "password": password, "email": email
      })
      .then((res) => {
        setCookie(document, "loggedUserName", res.data.username);
        this.refreshPage();
      })
      .catch((err) => this.handleErrors(err, modalTypes.SignUp));
  };

  signOut = () => {
    axios
      .get('/api/logout/')
      .then((res) => {
        removeCookie(document, "loggedUserName");
        this.refreshPage();
      })
      .catch((err) => console.log(err));
  };

  renderTagList = () => {
    return (
      <ButtonGroup >
        {
          this.state.allTags.map(tag => (
            <Button
              className="btn btn-secondary mb-2"
              key={"tag-filter-button-" + tag.id.toString()}
              name={tag.title}
              value={tag.id}
              style={
                {
                  "boxShadow": "none",
                  "backgroundColor": this.state.tagsSelected.includes(tag.id) ? "#333333" : "#6c757d",
                }
              }
              size="sm"
              active={this.state.tagsSelected.includes(tag.id)}
              onClick={() => this.selectTag(tag.id)}
            >
              {tag.title}
            </Button>
          ))
        }
      </ButtonGroup>
    )
  };

  renderTabList = () => {
    return (
      <div className="nav nav-tabs">
        <span
          className={this.state.viewCompleted ? "nav-link active" : "nav-link"}
          onClick={() => this.displayCompleted(true)}
        >
          Complete
        </span>
        <span
          className={this.state.viewCompleted ? "nav-link" : "nav-link active"}
          onClick={() => this.displayCompleted(false)}
        >
          Incomplete
        </span>
      </div>
    );
  };

  renderItems = () => {
    const { viewCompleted } = this.state;
    const newItems = this.state.todoList.filter(
      (item) => item.completed === viewCompleted
    );

    return newItems.map((item) => (
      <div key={"todo-" + item.id} className="mb-2">
        <li
          key={"todo-list" + item.id}
          className="list-group-item d-flex justify-content-between align-items-center"
        >
          <span
            className={`todo-title mr-2 ${this.state.viewCompleted ? "completed-todo" : ""
              }`}
            title={item.description}
          >
            {item.title}
          </span>
          <span>
            <button
              className="btn btn-secondary mr-2"
              onClick={() => this.editItem(item)}
            >
              Edit
            </button>
          </span>
        </li>
        <div className='ml-2'>
          {item.tags.map(tag => (
            <Badge
              key={"tag-badge-" + tag.id}
              className='mr-1'
              color="secondary"
              pill
            >
              {tag.title}
            </Badge>
          ))}
        </div>
      </div>
    ));
  };

  openModal = (modalType) => {
    this.setState({ openedModalType: modalType });
  };

  closeModal = () => {
    this.setState({ openedModalType: null });
  };

  renderOpenModal = () => {
    switch (this.state.openedModalType) {
      case modalTypes.SignIn:
      case modalTypes.SignUp:
        return (
          <LoginModal
            getErrors={this.getErrors}
            type={this.state.openedModalType}
            toggle={this.closeModal}
            onOK={this.handleLogin}
          />
        )
      case modalTypes.Todo:
        return (
          <TodoModal
            activeItem={this.state.activeItem}
            toggle={this.closeModal}
            onSaveItem={this.handleSubmitItem}
            onDeleteItem={this.handleDeleteItem}
          />
        )
      case modalTypes.Tags:
        return (
          <TagsModal
            allTags={this.state.allTags}
            toggle={this.closeModal}
            onDeleteTag={this.handleDeleteTag}
          />
        )
      case modalTypes.Warning:
        return (
          <WarningModal
            getErrors={this.getErrors}
            toggle={this.closeModal}
          />
        )
      default:
        return null
    }
  };

  render() {
    let loogedUserName = getCookies(document)['loggedUserName']
    return (
      <main className="container">
        <div className="d-flex justify-content-end mt-2">
          {
            loogedUserName ? (
              <span>
                <Badge
                  className='mr-2' color="secondary" pill
                >
                  {loogedUserName}
                </Badge>
                <button
                  className="btn btn-outline-secondary btn-sm mr-2"
                  onClick={this.signOut}
                >
                  Sign Out
                </button>
              </span>
            ) : (
              <span>
                <button
                  className="btn btn-outline-secondary btn-sm mr-2"
                  onClick={() => this.openModal(modalTypes.SignIn)}
                >
                  Sign In
                </button>
                <button
                  className="btn btn-outline-secondary btn-sm mr-2"
                  onClick={() => this.openModal(modalTypes.SignUp)}
                >
                  Sign Up
                </button>
              </span>
            )
          }
        </div>
        <h2 className="text-secondary text-uppercase text-center my-4">TODO</h2>
        <div className="row">
          <div className="col-md-6 col-sm-10 mx-auto p-0">
            <Card className="p-3">
              <div className="d-flex justify-content-between mb-4">
                <button
                  className="btn btn-primary"
                  onClick={this.createItem}
                >
                  ✚
                </button>
                <button
                  className="btn btn-primary"
                  onClick={() => this.openModal(modalTypes.Tags)}
                >
                  🀰
                </button>
              </div>
              {this.renderTagList()}
              {this.renderTabList()}
              <ul className="list-group list-group-flush border-top-0">
                {this.renderItems()}
              </ul>
            </Card>
          </div>
        </div>
        {this.renderOpenModal()}
      </main >
    );
  }
}

export default App;
