from fanfan.adapters.db.repositories.codes import CodesRepository
from fanfan.core.dto.code import CodeDTO
from fanfan.core.exceptions.codes import CodeNotFound
from fanfan.core.models.code import CodeId


class GetCodeById:
    def __init__(self, codes_repo: CodesRepository):
        self.codes_repo = codes_repo

    async def __call__(self, code_id: CodeId) -> CodeDTO:
        if code := await self.codes_repo.read_code_by_id(code_id):
            return code
        raise CodeNotFound
