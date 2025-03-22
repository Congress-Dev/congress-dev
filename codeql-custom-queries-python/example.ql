/**
 * This is an automatically generated file
 * @name Hello world
 * @kind problem
 * @problem.severity warning
 * @id python/example/hello-world
 */

import python

from Import imp
where imp.getAnImportedModuleName() = "zipfile"
select imp, imp.getLocation(), "File importing zipfile", "wut"