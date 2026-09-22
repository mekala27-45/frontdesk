"""Reject naive datetime constructors in application source."""
import ast
from pathlib import Path

def violations(paths: list[Path]) -> list[str]:
    if not paths:
        raise ValueError("No source inspected")
    errors=[]
    for path in paths:
        tree=ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node,ast.Call):
                name=ast.unparse(node.func)
                if name in {"datetime","datetime.now","datetime.combine","datetime.fromtimestamp"}:
                    minimum={"datetime.now":1,"datetime.fromtimestamp":2,"datetime.combine":3}.get(name,8)
                    if len(node.args)<minimum and not any(k.arg in {"tz","tzinfo"} for k in node.keywords):
                        errors.append(f"{path}:{node.lineno}")
                if name in {"datetime.utcnow","datetime.utcfromtimestamp"}:
                    errors.append(f"{path}:{node.lineno}")
    return errors

if __name__=="__main__":
    bad=violations(list(Path("packages").rglob("*.py")))
    if bad:
        raise SystemExit(str(bad))
    print("Timezone gate passed")

