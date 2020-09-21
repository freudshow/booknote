# fl

## sequence

```sequence
Title: 客户端，角色文案替换引擎，诱导引擎调用关系图
client->CharacterTextReplace:
Note over CharacterTextReplace:void *QCTRCreate(const char *filename)
Note over CharacterTextReplace:void QCTRDestroy(void *handle)
client->RG:
Note over RG:void QRouteGuidanceSetCTRHandle(void *rgHandle, void *CTRHandle)
Note over RG:void QRouteGuidanceSetCTRCharacter(void *rgHandle, char *characterName)
RG->CharacterTextReplace:文案替换调用
Note over CharacterTextReplace:void QCTRReplaceText(void *handle, char *characterName, unsigned short *from, unsigned short *to)
CharacterTextReplace-->RG:替换后文案
RG-->client:kRouteGuidanceEventActionPlayTTS
client->CharacterTextReplace:节日，gps，偏航
Note over CharacterTextReplace:void QCTRReplaceText(void *handle, char *characterName, unsigned short *from, unsigned short *to)
CharacterTextReplace-->client:替换后文案
Note right of CharacterTextReplace:m_mapCharacterMap key:char* name val:hash_map
Note right of CharacterTextReplace:m_mapCommon key:unsigned short* val:unsigned short*
Note right of CharacterTextReplace:m_map[0] key:unsigned short* val:unsigned short*
Note right of CharacterTextReplace:m_map[1] key:unsigned short* val:unsigned short*
Note right of CharacterTextReplace:m_map[...] key:unsigned short* val:unsigned short*
```