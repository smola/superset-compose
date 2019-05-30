package cmd

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/src-d/superset-compose/cmd/sandbox-ce/compose"
	"github.com/src-d/superset-compose/cmd/sandbox-ce/compose/workdir"

	"github.com/pkg/errors"
)

type installCmd struct {
	Command `name:"install" short-description:"Install and initialize containers" long-description:"Install, initialize, and start all the required docker containers, networks, volumes, and images.\n\nThe repos directory argument must point to a directory containing git repositories.\nIf it's not provided, the current working directory will be used."`

	Args struct {
		Reposdir string `positional-arg-name:"workdir"`
	} `positional-args:"yes"`
}

func (c *installCmd) Execute(args []string) error {
	reposdir, err := c.reposdirArg()
	if err != nil {
		return err
	}

	dir, err := workdir.Init(reposdir)
	if err != nil {
		return err
	}

	// Before setting a new workdir, stop the current containers
	compose.Run(context.Background(), "stop")

	err = workdir.SetActive(reposdir)
	if err != nil {
		return err
	}

	fmt.Printf("docker-compose working directory set to %s\n", dir)

	if err := compose.Run(context.Background(), "up", "--detach"); err != nil {
		return err
	}

	return OpenUI(time.Minute)
}

func (c *installCmd) reposdirArg() (string, error) {
	reposdir := c.Args.Reposdir
	reposdir = strings.TrimSpace(reposdir)

	var err error
	if reposdir == "" {
		reposdir, err = os.Getwd()
	} else {
		reposdir, err = filepath.Abs(reposdir)
	}

	if err != nil {
		return "", errors.Wrap(err, "could not get directory")
	}

	info, err := os.Stat(reposdir)
	if err != nil || !info.IsDir() {
		return "", fmt.Errorf("path '%s' is not a valid directory", reposdir)
	}

	return reposdir, nil
}

func init() {
	rootCmd.AddCommand(&installCmd{})
}
