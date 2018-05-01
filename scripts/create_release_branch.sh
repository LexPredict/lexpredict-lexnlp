#!/usr/bin/env bash

# ARGS:
# 1. '-core' repository DEVELOP branch name
# 2. '-lexnlp' repository OLD release branch name
# 3. '-lexnlp' repository NEW release branch name

CORE_REPO_PATH="/home/alex/dev/michael/contraxsuite/lexpredict-contraxsuite-core"
LEXNLP_REPO_PATH="/home/alex/dev/michael/contraxsuite/lexpredict-lexnlp"
DEV_BRANCH=$1
OLD_RELEASE_BRANCH=$2
NEW_RELEASE_BRANCH=$3
aline="================================================================="

# prompt
if [ $# -ne 3 ]; then
    read -p "Enter '-core' repository DEVELOP branch name: " DEV_BRANCH
    if [ -z ${DEV_BRANCH} ]; then
        echo "Exiting program."
        return 1
    fi
    read -p "Enter '-lexnlp' repository OLD release branch name: " OLD_RELEASE_BRANCH
    if [ -z ${OLD_RELEASE_BRANCH} ]; then
        echo "Exiting program."
        return 1
    fi
    read -p "Enter '-lexnlp' repository NEW release branch name: " NEW_RELEASE_BRANCH
    if [ -z ${NEW_RELEASE_BRANCH} ]; then
        echo "Exiting program."
        return 1
    fi
fi

# confirm further processing
echo ${aline}
echo "Copy data from core@${DEV_BRANCH} to lexnlp@${NEW_RELEASE_BRANCH}, continue?" yn
select yn in "Yes" "No"; do
    case ${yn} in
        Yes ) break;;
        No ) return 1;;
    esac
done

# check if develop branch exists
echo ${aline}
echo "Update core@${DEV_BRANCH}"

pushd ${CORE_REPO_PATH}

if [ -z "`git branch --list ${DEV_BRANCH}`" ]
then
   echo "'-core' branch ${DEV_BRANCH} doesn't exist. Exiting program."
   return 1
fi
git pull origin ${DEV_BRANCH}

# replace old release number with new one
echo ${aline}
echo "Update version number in core@${DEV_BRANCH} from ${OLD_RELEASE_BRANCH} to ${NEW_RELEASE_BRANCH}"

OLD_RELEASE_BRANCH_esc=$(echo ${OLD_RELEASE_BRANCH} | sed 's,\.,\\.,g')
NEW_RELEASE_BRANCH_esc=$(echo ${NEW_RELEASE_BRANCH} | sed 's,\.,\\.,g')
find ./ -type f -readable -writable -exec sed -i "s/__version__ = \"$OLD_RELEASE_BRANCH_esc\"/__version__ = \"$NEW_RELEASE_BRANCH_esc\"/g" {} \;
find setup.py -type f -readable -writable -exec sed -i "s/version='$OLD_RELEASE_BRANCH_esc'/version='$NEW_RELEASE_BRANCH_esc'/g" {} \;

echo ${aline}
echo "Update version number in core@${DEV_BRANCH} from ${OLD_RELEASE_BRANCH} to ${NEW_RELEASE_BRANCH}"
git add --all
git commit -m "CS: updated version from ${OLD_RELEASE_BRANCH} to ${NEW_RELEASE_BRANCH}"
git push origin ${DEV_BRANCH}

popd

echo ${aline}
echo "Update lexnlp@${OLD_RELEASE_BRANCH}"

pushd ${LEXNLP_REPO_PATH}

# check old release branch exists, checkout
if [ -z "`git branch --list ${OLD_RELEASE_BRANCH}`" ]
then
   echo "'-lexnlp' branch ${OLD_RELEASE_BRANCH} doesn't exist. Exiting program."
   return 1
fi

git fetch origin ${OLD_RELEASE_BRANCH}
git checkout ${OLD_RELEASE_BRANCH}

# check that new release branch exists, checkout/create
echo ${aline}
echo "Create lexnlp@${NEW_RELEASE_BRANCH}"

if [ -z "`git branch --list ${NEW_RELEASE_BRANCH}`" ]
then
   echo "'-lexnlp' branch ${NEW_RELEASE_BRANCH} doesn't exist. Creating branch."
   git checkout -b ${NEW_RELEASE_BRANCH}
else
   git checkout ${NEW_RELEASE_BRANCH}
fi

# copy files from develop to new branch
echo ${aline}
echo "Copy files from -core to -lexnlp local repo"

cp -rf ${CORE_REPO_PATH}/lexnlp ${LEXNLP_REPO_PATH}
cp -rf ${CORE_REPO_PATH}/libs ${LEXNLP_REPO_PATH}
cp -rf ${CORE_REPO_PATH}/scripts ${LEXNLP_REPO_PATH}
cp -rf ${CORE_REPO_PATH}/test_data ${LEXNLP_REPO_PATH}
cp -rf ${CORE_REPO_PATH}/python-requirements* ${LEXNLP_REPO_PATH}
cp -rf ${CORE_REPO_PATH}/setup.py ${LEXNLP_REPO_PATH}
cp -rf ${CORE_REPO_PATH}/MANIFEST.in ${LEXNLP_REPO_PATH}

# create commit and push
echo ${aline}
echo "Commit and push new branch to -lexnlp remote repo"
git add --all
git commit -m "initial ${NEW_RELEASE_BRANCH} commit"
git push origin ${NEW_RELEASE_BRANCH}

# update master
echo ${aline}
echo "Update master branch in -lexnlp remote repo"
git checkout master
git pull origin master
git merge ${NEW_RELEASE_BRANCH}
git push origin master

popd
