from dataclasses import dataclass

@dataclass(frozen=True)
class Track:
    name: str
    uri: str

    def __eq__(self, other):
        if isinstance(other, Track):
            return self.name == other.name
        return NotImplemented

    def __hash__(self):
        return hash(self.name)

    def to_dict(self):
        return {
            'name': self.name,
            'uri': self.uri
        }

