from github import Github
#g = Github("access_token")
g = Github("")
user=g.get_user()
login=user.login
print(user)
print(login)
#for repo in g.get_user().get_repos():
    #print(repo.name)

def createRepo(name):
    user.create_repo(name)

def push_init(filenames):
    temp=filenames.split()
    print(temp)
    r_name=input("enter repo name:")
    files=temp
    print(login+"/"+r_name)
    try:
        repo = g.get_repo(login+"/"+r_name)
        print(repo)
    except:
        print("repository doesn't exist")
    try:
        branch_name=input("Enter the branch name:")
        for one_file in files:
            file_content = repo.get_contents(one_file,ref=branch)
            data = file_content.decoded_content.decode("utf-8")
            update_data=open(one_file, "r")
            data+=update_data.read()
            push(one_file, "test commit", data, branch_name,repo)
    except:
        print("file or branch does not exist")
        for one_file in files:
            update_data=open(one_file, "r")
            data=update_data.read()
            push(one_file, "Test commit", data, branch_name,repo)

def push(path, message, content, branch,repo,update=False):
    source = repo.get_branch("main")
    try:
        repo.create_git_ref(ref=f"refs/heads/{branch}", sha=source.commit.sha)
    except:
        print("branch already exists")
    if update:  # If file already exists, update it
        contents = repo.get_contents(path, ref=branch)  # Retrieve old file to get its SHA and path
        repo.update_file(contents.path, message, content, contents.sha, branch=branch)
        print("updated a file")# Add, commit and push branch
    else:  # If file doesn't exist, create it
        repo.create_file(path, message, content, branch=branch)
        print("created a file")# Add, commit and push branch

#push(file_path, "Add pytest to dependencies.", data, "update-dependencies", update=True)
#repo = g.get_repo("harsha7108/Machine-intelligence")
#contents = repo.get_contents("")
#while contents:
    #file_content = contents.pop(0)
    #if file_content.type == "dir":
        #print(contents)
        #contents.extend(repo.get_contents(file_content.path))
        #print(contents)
        #print(file_content)
    #else:
        #print(file_content)

files=input("enter file path: ")
push_init(files)

